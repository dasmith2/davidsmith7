from djaveTest import TestCase, get_test_user
from djaveTeam.models import Team, TeamMember, TeamAPIKey


def get_test_team(**kwargs):
  return Team.live.create(name=kwargs.get('name', 'My test team'))


def get_test_team_member(**kwargs):
  team = kwargs.get('team', None)
  if not team:
    team = get_test_team(**kwargs)
  user = kwargs.get('user', None)
  if not user:
    user = get_test_user(**kwargs)
  return TeamMember.live.create(user=user, team=team)


class TeamAPIKeyTest(TestCase):
  def test_create(self):
    team = get_test_team()
    api_key = TeamAPIKey.objects.create_key(team, 'My test key')
    plain_password = api_key.get_plain_password()
    self.assertEqual(team, TeamAPIKey.objects.get_team(
        api_key.username, plain_password))
