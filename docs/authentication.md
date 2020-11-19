
## ubiops signin

**Description:**

Sign in using your credentials.

If you want to use a service token, use the <token> flag option.

**Arguments:** - 

**Options:**
- [binary option] `--bearer`

  Sign in with email and password [default]
- [binary option] `--token`

  Sign in with a service token
- `--api`

  The API endpoint of UbiOps
- `-e`/`--email`

  E-mail to sign in with. User will be prompted if not specified and <token> option is not given
- `-p`/`--password`

  Password to sign in with. User will be prompted if not specified. If <token> option is given, use a service token formatted like `"Token 1abc2def3ghi4jkl5mno6pqr7stu8vwx9yz"`.

## ubiops status

**Description:**

Whether the current user is authorized or not.

**Arguments:** - 

**Options:** - 

## ubiops user
### ubiops user get

**Description:**

Show the email of the current user.

**Arguments:** - 

**Options:** - 

### ubiops user set

**Description:**

Change the user interacting with the CLI.

**Arguments:**
- [required] `email`

**Options:** - 

## ubiops signout

**Description:**

Sign out of the CLI.

**Arguments:** - 

**Options:** - 
