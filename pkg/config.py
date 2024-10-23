from os import getenv

user = getenv('CRYPTOWEB_USER')
password = getenv('CRYPTOWEB_PWD')
database = getenv('CRYPTOWEB_DB')
host = getenv('CRYPTOWEB_HOST')


SECRET_KEY="R5T6Y7UHJIKOLO987EROELFKGWASDDJNRFTGHVN"
ADMIN_EMAIL="godspowerlawrence008@gmail.com"
USER_PROFILE_PATH="pkg/static/profiles/"
# SQLALCHEMY_DATABASE_URI=f'mysql+mysqlconnector://{user}:{password}@{host}/{database}'
SQLALCHEMY_DATABASE_URI="mysql+mysqlconnector://lawrence:1234@127.0.0.1:8889/goldcrypto"

