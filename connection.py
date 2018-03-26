import getpass
import re
import requests


class Connection:
    login = 'https://sso.garmin.com/sso/login'
    check = 'https://connect.garmin.com/user/username'
    session = 'https://connect.garmin.com/legacy/session'
    file_upload =\
        'https://connect.garmin.com/modern/proxy/upload-service/upload'
    main = 'https://connect.garmin.com/modern/'

    def __init__(self):
        self.session = requests.Session()

    def authenticate(self):
        try:
            ticket = self.__phase_one()
            self.__phase_two(ticket)
            self.__phase_three()
        except Exception:
            return False
        return True

    def upload_activity(self, filename):
        files = {'file': (filename, open(filename, 'rb'))}
        url = Connection.file_upload + '/fit'
        resp = self.session.post(url, files=files, headers={'NK': 'NT'})

        if resp.status_code not in (200, 201, 409):
            raise Exception('Unable to upload file!')
        print(filename + ' uploaded successfully!')

    def __check_login(self, page):
        garmin_user = page.json()
        username = garmin_user.get('username')
        if not page.ok or not username:
            raise Exception('Not logged in!')
        print('Logged in as {}'.format(username))

    def __phase_one(self):
        params = {'service': Connection.main}
        # [TODO] Take login & pass from file
        username = input('Login: ')
        password = getpass.getpass('Password: ')
        data = {'embed': 'false', 'username': username, 'password': password}
        resp = self.session.post(Connection.login,
                                 params=params,
                                 data=data)
        if resp.status_code != 200:
            raise Exception('Website is down')
        if 'GARMIN-SSO-GUID' not in self.session.cookies:
            raise Exception('Missing cookie')
        ticket = self.__retrieve_ticket(resp)
        return ticket

    def __phase_two(self, ticket):
        params = {'ticket': ticket}
        self.session.get(Connection.main, params=params)
        self.session.get(Connection.session)

    def __phase_three(self):
        res = self.session.get(Connection.check)
        self.__check_login(res)

    def __retrieve_ticket(self, resp):
        regex = 'var response_url(\s+)= (\"|\').*?ticket=(?P<ticket>[\w\-]+)(\"|\')'
        ticket = re.search(regex, resp.text)
        if not ticket:
            raise Exception('Missing ticket')
        return ticket.group('ticket')
