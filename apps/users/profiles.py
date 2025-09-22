import json

import requests
from django.conf import settings
from django.contrib.auth import get_user_model

PROFILE_PHOTO_FORMAT = getattr(settings, 'USO_PROFILE_PHOTO_FORMAT', 'webp')


class ExternalProfileManager:
    PROFILE_FIELDS = []

    @classmethod
    def create_username(cls, profile: dict) -> str:
        """
        Create a username for a new user.
        In this version, the username is always the email address.

        :param profile: dictionary containing first_name, last_name, and email
        :return: username string (must be unique)
        :raises ValueError: if required fields are missing or username already exists
        """
        User = get_user_model()

        # Required fields check
        if 'first_name' in profile and 'last_name' in profile and 'email' in profile:
            username = profile['email'].lower()

            # If the email is already used as a username, raise an error
            if User.objects.filter(username=username).exists():
                raise ValueError(f"Username '{username}' already exists.")

            return username
        else:
            raise ValueError('First name, last name, and email are required to create a username.')



    @classmethod
    def fetch_profile(cls, username: str) -> dict:
        """
        Called to fetch a user profile from the remote source. This is used to sync the specified user's
        profile from the remote source to the local database. Only fields specified in PROFILE_FIELDS will be changed in
        the User model.
        :param username: username of the user to fetch
        :return: dictionary of profile parameters
        """
        return {}

    @classmethod
    def create_profile(cls, profile: dict) -> dict:
        """
        Called to create a new profile in the remote source. User is expected to not exist in the remote source.
        :param profile: Dictionary of profile parameters.
        """
        return {}

    @classmethod
    def update_profile(cls, username, profile: dict, photo=None) -> bool:
        """
        Called to update the profile in the remote source. User is expected to exist in the remote source.

        :param profile: Dictionary of profile parameters.
        :param photo: File-like object of the user's photo
        :param username: username of the user to update
        :return: True if successful, False otherwise.
        """
        return True

    @classmethod
    def fetch_new_users(cls) -> list[dict]:
        """
        Fetch new users from the remote source. This is used to sync new users from the remote source to the local database.
        :return: list of dicts, one per user.
        """
        return []

    @classmethod
    def get_user_photo_url(cls, username: str):
        return f'{settings.MEDIA_URL}/photo/{username}.{PROFILE_PHOTO_FORMAT}'


class RemoteProfileManager(ExternalProfileManager):
    PROFILE_FIELDS = [
        'title', 'first_name', 'last_name', 'preferred_name', 'emergency_phone', 'other_names',
        'email', 'username', 'roles', 'permissions', 'emergency_contact',
    ]

    USER_PHOTO_URL = '{username}/photo'
    USER_PROFILE_URL = '{username}'
    USER_CREATE_URL = ''
    USER_LIST_URL = ''
    API_HEADERS = {'Content-Type': 'application/json'}

    SSL_VERIFY_CERTS = True

    @classmethod
    def fetch_profile(cls, username: str):
        url = cls.USER_PROFILE_URL.format(username=username)
        r = requests.get(url, headers=cls.API_HEADERS, verify=cls.SSL_VERIFY_CERTS)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return {}

    @classmethod
    def create_profile(cls, profile: dict):
        data = {field: profile[field] for field in cls.PROFILE_FIELDS if field in profile}
        r = requests.post(cls.USER_CREATE_URL, json=data, headers=cls.API_HEADERS, verify=cls.SSL_VERIFY_CERTS)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            return {}

    @classmethod
    def update_profile(cls, username: str, profile: dict, photo=None):
        data = {field: profile[field] for field in cls.PROFILE_FIELDS if field in profile}
        url = cls.USER_PROFILE_URL.format(username=username)
        if photo:
            files = {'photo': (photo.name, photo, photo.content_type)}
            r = requests.patch(url, files=files, json=data, headers=cls.API_HEADERS, verify=cls.SSL_VERIFY_CERTS)
        else:
            r = requests.patch(url, json=data, headers=cls.API_HEADERS, verify=cls.SSL_VERIFY_CERTS)
        if r.status_code == requests.codes.ok:
            return True
        else:
            return False

    @classmethod
    def fetch_new_users(cls) -> list[dict]:
        r = requests.get(cls.USER_LIST_URL, headers=cls.API_HEADERS, verify=cls.SSL_VERIFY_CERTS)
        if r.status_code == requests.codes.ok:
            return r.json()['results']
        else:
            return []

    @classmethod
    def get_user_photo_url(cls, username: str):
        return cls.USER_PHOTO_URL.format(username=username)


