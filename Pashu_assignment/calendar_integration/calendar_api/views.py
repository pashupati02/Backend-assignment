from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from google.auth import exceptions as google_auth_exceptions
from google.oauth2 import credentials as google_credentials
from google_auth_oauthlib.flow import Flow


class GoogleCalendarInitView(View):
    def get(self, request):
        # Step 1: Start OAuth flow
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        request.session['oauth2_state'] = state
        return redirect(authorization_url)


class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Step 2: Handle OAuth redirect
        state = request.session.get('oauth2_state')
        if not state or state != request.GET.get('state'):
            return HttpResponse('Invalid state parameter', status=400)
        flow = Flow.from_client_secrets_file(
            settings.GOOGLE_CLIENT_SECRETS_FILE,
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri(reverse('google-calendar-redirect'))
        )
        try:
            flow.fetch_token(
                authorization_response=request.build_absolute_uri(),
            )
        except google_auth_exceptions.OAuth2Error:
            return HttpResponse('Error retrieving access token', status=400)
        credentials = flow.credentials
        # Use the credentials to make API requests
        # Implement the code to get a list of events from the user's calendar using the credentials
        # Example code to get a list of events:
        # service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)
        # events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        # events = events_result.get('items', [])
        return HttpResponse('Successfully retrieved access token and events')
