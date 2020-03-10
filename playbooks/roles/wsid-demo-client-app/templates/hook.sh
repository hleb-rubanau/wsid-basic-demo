#! /bin/bash
# this is fairly simplistic deployer, which only copies data to location 
# from where files could be read by www-data
# but there could be pretty anything -- contents of sourcefile could be pushed to redis, supplied to login utility etc.

SOURCE_DIRECTORY="{{ wsid_var_run }}/private/{{wsid_demo_identity }}"
TARGET_DIRECTORY="{{ wsid_demo_client_app_data_dir }}"
TARGET_FILE={{ hook.file }}

function deploy_file() {
    local fname="$1"
    local srcpath="$SOURCE_DIRECTORY/$fname"
    local targetpath="$TARGET_DIRECTORY/$fname"

    mkdir -p "$TARGET_DIRECTORY"    
    chown www-data "$TARGET_DIRECTORY"
    chmod 0500 "$TARGET_DIRECTORY"

    touch "$targetpath"
    chown www-data "$targetpath"
    chmod 0400 "$targetpath"
    cat "$srcpath" > "$targetpath"
}

deploy_file "$TARGET_FILE" 
