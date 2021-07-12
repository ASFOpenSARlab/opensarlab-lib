from getpass import getpass

from IPython.display import clear_output

from asf_hyp3 import API, LoginError


class EarthdataLogin:

    def __init__(self, username=None, password=None):

        """
        takes user input to login to NASA Earthdata
        updates .netrc with user credentials
        returns an api object
        note: Earthdata's EULA applies when accessing ASF APIs
              Hyp3 API handles HTTPError and LoginError
        """
        err = None
        while True:
            if err: # Jupyter input handling requires printing login error here to maintain correct order of output.
                print(err)
                print("Please Try again.\n")
            if not username or not password:
                print(f"Enter your NASA EarthData username:")
                username = input()
                print(f"Enter your password:")
                password = getpass()
            try:
                api = API(username) # asf_hyp3 function
            except Exception:
                raise
            else:
                try:
                    api.login(password)
                except LoginError as e:
                    err = e
                    clear_output()
                    username = None
                    password = None
                    continue
                except Exception:
                    raise
                else:
                    clear_output()
                    print(f"Login successful.")
                    print(f"Welcome {username}.")
                    self.username = username
                    self.password = password
                    self.api = api
                    break


    def login(self):
        try:
            self.api.login(self.password)
        except LoginError:
            raise

