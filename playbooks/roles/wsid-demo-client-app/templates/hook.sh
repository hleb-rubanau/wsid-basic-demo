#! /bin/bash
    
WSID_PASSWD_FILE="{{ wsid_var_run }}/private/{{wsid_demo_identity}}/passwd"
WSID_KEY_FILE="{{ wsid_var_run }}/private/{{ wsid_demo_identity }}/id_ed25519"
SECRETS_FILE="{{ wsid_demo_client_app_installation_dir }}/secrets.py"

cat > "$SECRETS_FILE" <<SECRETSFILE
SECRET_PASSWORD="$(cat "$WSID_PASSWD_FILE")"
SECRET_SSH_KEY_BODY="""$(cat "$WSID_KEY_FILE")
"""
SECRETSFILE

chmod g+r-w "$SECRETS_FILE"
chown :www-data "$SECRETS_FILE"
echo "Regenerated $SECRETS_FILE, reloading emperor" >&2

/usr/sbin/service uwsgi-emperor reload 
