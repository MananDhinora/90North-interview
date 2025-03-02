import json
import os
import secrets
import tempfile
import io

# Third-party imports
import requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, FileResponse
from django.shortcuts import redirect, render, reverse


# Local imports
from .models import RefreshToken

# Configuration settings

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = (
    "1"  # to handle oauth2callback without https
)
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.metadata",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid",
]
API_SERVICE_NAME = "drive"
API_VERSION = "v3"


def index(request):
    """Render the index page."""
    return render(request, "index.html")


def google_picker(request):
    """Render the Google Picker page."""
    if "credentials" not in request.session:
        return redirect("authorize")
    return render(
        request, "google_picker.html", {"google_client_id": settings.GOOGLE_CLIENT_ID}
    )


def google_picker_callback(request):
    """Handle the callback from the Google Picker."""
    if request.method != "POST":
        return HttpResponse("Invalid request method.")

    # Process the data from the Google Picker
    data = request.POST.get("data")
    selected_files = json.loads(data)
    selected_file_ids = {file["id"]: file["name"] for file in selected_files["docs"]}
    return JsonResponse(data=selected_file_ids)


def upload_file(request):
    """Upload a file to Google Drive using the user's refresh token."""
    if request.method != "POST":
        return HttpResponse("Method not allowed.")

    myfile = request.FILES.get("myfile")

    if not myfile:
        return HttpResponse("No file was uploaded.")

    if "credentials" not in request.session:
        return HttpResponse("User not authenticated. Please authorize first.")

    # Get user's refresh token
    try:
        refresh_token = RefreshToken.objects.get(
            user=User.objects.get(username=request.session.get("user_info")["name"])
        ).refresh_token
    except RefreshToken.DoesNotExist:
        return HttpResponse("Refresh token not found.")
    except User.DoesNotExist:
        return HttpResponse("User not found.")
    except KeyError:
        return HttpResponse("User info not found in session.")

    if not refresh_token:
        return HttpResponse("Refresh token not found.")

    try:
        # Build Google Drive service
        service = build(
            API_SERVICE_NAME,
            API_VERSION,
            credentials=Credentials(
                token=None,
                refresh_token=refresh_token,
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET,
                token_uri="https://oauth2.googleapis.com/token",
            ),
        )

        # Prepare file metadata
        file_metadata = {
            "name": myfile.name,
            "mimeType": myfile.content_type,
        }

        # Create a temporary file - do not delete
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file_path = temp_file.name

        # Write uploaded file to temporary file
        for chunk in myfile.chunks():
            temp_file.write(chunk)
        temp_file.flush()
        temp_file.close()

        # Upload to Google Drive
        media = MediaFileUpload(
            temp_file_path,
            mimetype=myfile.content_type,
            resumable=True,
        )

        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )

        return HttpResponse(
            f'File "{myfile.name}" uploaded to Google Drive with ID: {file.get("id")}'
        )

    except HttpError as error:
        return HttpResponse(f"An error occurred: {error}")
    except Exception as e:
        return HttpResponse(f"An unexpected error occurred: {e}")


def download_file(request):
    try:
        refresh_token = RefreshToken.objects.get(
            user=User.objects.get(username=request.session.get("user_info")["name"])
        ).refresh_token

        credentials = Credentials(
            token=None,
            refresh_token=refresh_token,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            token_uri="https://oauth2.googleapis.com/token",
        )

        service = build("drive", "v3", credentials=credentials)
        file_id = request.POST.get("file_id")

        request_file = service.files().get_media(fileId=file_id)
        file = io.BytesIO()
        downloader = MediaIoBaseDownload(file, request_file)

        done = False
        while done is False:
            status, done = downloader.next_chunk()

        file.seek(0)

        file_metadata = service.files().get(fileId=file_id).execute()
        filename = file_metadata["name"]

        return FileResponse(file, as_attachment=True, filename=filename)

    except HttpError as error:
        return HttpResponse(f"An error occurred: {error}", status=500)

    except Exception as e:
        return HttpResponse(f"An unexpected error occurred: {e}", status=500)


def authorize(request):
    """Begin the OAuth2 authorization flow."""
    flow = Flow.from_client_secrets_file(settings.CLIENT_SECRETS_FILE, scopes=SCOPES)
    flow.redirect_uri = request.build_absolute_uri(reverse("oauth2callback"))
    state = secrets.token_urlsafe(32)
    authorization_url, _ = flow.authorization_url(
        access_type="offline", include_granted_scopes="true", state=state
    )
    request.session["state"] = state
    next_url = request.GET.get("next", "index")
    request.session["next_url"] = next_url
    return redirect(authorization_url)


def oauth2callback(request):
    """Handle the OAuth2 callback from Google."""
    state = request.session.get("state")
    received_state = request.GET.get("state")
    if state != received_state:
        return HttpResponse("State does not match. CSRF Attack Likely")

    flow = Flow.from_client_secrets_file(
        settings.CLIENT_SECRETS_FILE, scopes=SCOPES, state=state
    )
    flow.redirect_uri = request.build_absolute_uri(reverse("oauth2callback"))
    authorization_response = request.build_absolute_uri()
    flow.fetch_token(authorization_response=authorization_response)

    # Store credentials and user info
    credentials = flow.credentials
    request.session["credentials"] = credentials_to_dict(credentials)
    request.session["features"] = check_granted_scopes(credentials)

    # Get user information
    user_info = (
        flow.authorized_session()
        .get("https://www.googleapis.com/oauth2/v1/userinfo")
        .json()
    )
    request.session["user_info"] = user_info

    # Create or get user
    username = user_info.get("name")
    if " " in username:
        username =  username.replace(" ", "")

    email = user_info.get("email")
    password = user_info.get("email")  # Note: Using email as password is not secure

    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        try:
            user = User.objects.create_user(
                username=username, email=email, password=password
            )
            user.save()
        except Exception as e:
            messages.error(request, f"Error creating user: {e}")
            return redirect(request.session.get("next_url", "index"))

    # Save or update refresh token
    try:
        refresh_token_obj, created = RefreshToken.objects.get_or_create(
            user=user,
            defaults={"refresh_token": request.session["credentials"]["refresh_token"]},
        )
        if not created:
            refresh_token_obj.refresh_token = request.session["credentials"][
                "refresh_token"
            ]
            refresh_token_obj.save()

    except Exception as e:
        messages.error(request, f"Error creating/updating refresh token: {e}")

    return redirect(request.session.get("next_url", "index"))


def revoke(request):
    """Revoke the user's OAuth token."""
    if "credentials" not in request.session:
        return HttpResponse(
            'You need to <a href="/authorize">authorize</a> before testing the code to revoke credentials.'
        )

    credentials_dict = request.session["credentials"]
    credentials = Credentials(**credentials_dict)

    revoke = requests.post(
        "https://oauth2.googleapis.com/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    status_code = getattr(revoke, "status_code")
    if status_code == 200:
        return HttpResponse(
            'Credentials successfully revoked.<br><br><a href="/google">Back</a>'
        )
    else:
        return HttpResponse('An error occurred.<br><br><a href="/google">Back</a>')


def clear_credentials(request):
    """Clear the credentials from the session."""
    if "credentials" in request.session:
        del request.session["credentials"]
    return HttpResponse(
        'Credentials have been cleared.<br><br><a href="/google">Back</a>'
    )


def credentials_to_dict(credentials):
    """Convert OAuth credentials to a dictionary."""
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "granted_scopes": credentials.granted_scopes,
    }


def check_granted_scopes(credentials):
    """Check which scopes were granted in the OAuth flow."""
    features = {}
    features["drive"] = (
        "https://www.googleapis.com/auth/drive.metadata.readonly"
        in credentials.granted_scopes
    )
    return features


def get_auth_token(request):
    """Return the OAuth token for authenticated users."""
    if "credentials" not in request.session:
        return JsonResponse({"authenticated": False}, status=401)

    credentials_dict = request.session["credentials"]
    return JsonResponse({"authenticated": True, "token": credentials_dict["token"]})
