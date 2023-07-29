"""
Tests for tags APIs.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status  # HTTP status codes
from rest_framework.test import APIClient  # testing client

from core.models import Tag

from recipe.serializers import TagSerializer


# tags api that can be used in tests
TAGS_URL = reverse('recipe:tag-list')


def create_user(email='user@example.com', password='testpass123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


def detail_url(tag_id):
    """Create and return a tag detail URL."""

    # generate a unique URL for a specific recipes detail endpoint.
    return reverse('recipe:tag-detail', args=[tag_id])


# test as unauthenticated user
class PublicTagsAPITests(TestCase):
    """Test unauthenticated API requests."""

    # create a test client for this class (unauthentiacted)
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call tags API (getting tags)."""

        res = self.client.get(TAGS_URL)

        # check that status code is HTTP 401
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test authenticated API requests."""

    # creates client and user
    # then authenticates client with that user
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""

        # create 2 tags in db
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        # assign value to a response that will make request to the API
        res = self.client.get(TAGS_URL)

        # retrieve all the tags (2 here)
        # sort tags by namess in reverse order (last updated shows 1st)
        tags = Tag.objects.all().order_by('-name')

        # pass all retrieved tags to a serializer
        # result should match whatever serializer returns
        # many=True: when passing a list of items (2 here)
        serializer = TagSerializer(tags, many=True)

        # check that status is successful
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check that data dict that was returned in the response
        # is equal to the data dict of the object passed through serializer
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""

        user2 = create_user(email='user2@example.com')

        # create 2 tags for diff users
        Tag.objects.create(user=user2, name='Fruity')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')

        # make request to the API from self.user
        res = self.client.get(TAGS_URL)

        # Note: no serializer

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # check if only 1 tag is returned in response
        self.assertEqual(len(res.data), 1)
        # for the 1st resukt of data, the name should be
        # same as name for tag auth user
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_create_tag(self):
        """Test creating a tag throught the API."""
        pass

    def test_update_tag_name(self):
        """Test update tag name."""

        tag = Tag.objects.create(user=self.user, name='Breakfast')

        payload = {'name': 'Dinner'}

        # generate a url for a tag with that id
        url = detail_url(tag.id)

        # assign value to a response that will make request to the API
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # refreshed tag object in db
        tag.refresh_from_db()

        self.assertEqual(tag.name, payload['name'])
        self.assertEqual(tag.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the tags user returns in an error."""
        pass

    def test_delete_tag(self):
        """Test deleting a tag successful."""
        pass

    def test_delete_other_users_tags_error(self):
        """Test trying to delete another users tag gives error."""
        pass