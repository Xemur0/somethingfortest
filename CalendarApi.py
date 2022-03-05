from __future__ import print_function
import datetime
import googleapiclient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from config import calendarId, SERVICE_ACCOUNT_FILE
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendar:
    """
    Connect to API Calendar Google
    """
    def __init__(self):
        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        self.service = googleapiclient.discovery.build('calendar', 'v3', credentials=credentials)

    def create_event_dict(self, id, year, month, day):
        """
        create a dictionary with info
        :return:
        """
        event = {
            'summary': id,
            'description': f'https://t.me/{id}',
            'start': {
                'dateTime': f'{year}-{month}-{day}T20:00:00+03:00',
            },
            'end': {
                'dateTime': f'{year}-{month}-{day}T21:30:00+03:00',
            }
        }
        return event

    def create_event(self, event):
        """
        Create event
        """
        e = self.service.events().insert(calendarId=calendarId,
                                         body=event).execute()
        print('Event created: %s' % (e.get('id')))

    def get_events_list(self):
        """
        Show events
        """
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = self.service.events().list(calendarId=calendarId,
                                                   timeMin=now,
                                                   maxResults=10, singleEvents=True,
                                                   orderBy='startTime').execute()
        events = events_result.get('items', [])
        result = []
        if not events:
            return 'No upcoming events found.'

        for event in events:
            result.append([event['summary'], event['start']['dateTime']])
        return result
