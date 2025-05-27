#######################
### CUSTOM COMMANDS ###
#######################

####################
# remove conda env #
####################
custom_conda_rmv() {
    # Check for env name
    if [ -z "$1" ]; then
        echo "Please provide the environment name to remove."
        return 1
    fi

    # Store env name
    ENV_NAME="$1"
    # Activate env
    conda activate "$ENV_NAME" || return 1

    # Confirmation
    read -p "Confirm remove $ENV_NAME? (y/n): " confirmation
    if [[ ! "$confirmation" =~ ^[Yy]$ ]]; then
        echo "Operation canceled. Environment '$ENV_NAME' was not removed."
        return 0
    fi

    # Uninstall pip packages (ignore error if no pip packages)
    echo "Removing pip packages..."
    pip uninstall -q -r <(conda list | awk '/pypi/ {print $1}') -y

    # Deactivate and remove env
    conda deactivate
    conda remove -n "$ENV_NAME" --all -y

    echo "Environment $ENV_NAME removed."
}

# only add alias if command does not exsist
if command -v condarmv &> /dev/null; then
    echo "Error: the 'condarmv' command already exsists. Did not overwrite with custom command."
else 
    alias condarmv="custom_conda_rmv"
fi

#######################################
# check git status in Software folder #
#######################################
#custom_git_status() {
#    for d in ~/Software/*/; do
#        echo -n "$(basename "$d"): ";
#        git -C "$d" status | tail -n 1;
#    done
#}

custom_git_status() {
    # Find max repo name length for alignment ( ((X)) used for numerical comparisons)
    max_length=0
    for d in ~/Software/*/; do
        repo_name=$(basename "$d")
        (( ${#repo_name} > max_length )) && max_length=${#repo_name}
    done

    # Loop through all repos and print formatted output
    for d in ~/Software/*/; do
        repo_name=$(basename "$d")

        # Check if it's a Git repository
        if [ ! -d "$d/.git" ]; then
            printf "%-*s\t%s\t%s\n" "$max_length" "$repo_name" "❌" "Not a Git repository"
            continue
        fi

        # Get the current branch (-C to run command in $d directory without cd)
        branch=$(git -C "$d" rev-parse --abbrev-ref HEAD 2>/dev/null)

        # Get Git status information (porcelain for scripting output, vs human-readable)
        status_output=$(git -C "$d" status --porcelain)

        # Count modified and untracked files
        modified_files=$(echo "$status_output" | grep "^ M " | wc -l)  # Modified files
        untracked_files=$(echo "$status_output" | grep "^?? " | wc -l) # Untracked files

        # Determine output message
        # No modified/untracked files = clean repo
        if (( modified_files == 0 && untracked_files == 0 )); then
		emoji="✅"
		status_msg="Clean"
        # Print number of modified/untracked files
        else
		emoji=""
		status_msg=""
		(( modified_files > 0 )) && { emoji+="⚠️  "; status_msg="$modified_files modified file(s)"; }
		# "X:+$X | " = if X is not empty, replace it with "X | "
		(( untracked_files > 0 )) && { emoji+="🆕  "; status_msg="${status_msg:+$status_msg | }$untracked_files untracked file(s)"; }
        fi

        # Print aligned output (%-*s = left align, max_length width, repo_name)
        printf "%-*s\t%s\t%s (on branch %s)\n" "$max_length" "$repo_name" "$emoji" "$status_msg" "$branch"
    done
}

# only add alias if command does not exsist
if command -v gss &> /dev/null; then
    echo "Error: the 'gss' command already exsists. Did not overwrite with custom command."
else
    alias gss="custom_git_status"
fi

#################################
# add large files to .gitignore #
#################################
custom_git_ignore() {
    # Get the git root directory, will have error if not in git repo
    git_root=$(git rev-parse --show-toplevel) || return 1

    # Find files larger than 100 MB (GitHub limit), excluding .git folder
    # sed command removes leading './'
    large_files=$(find "$git_root" -type f -size +100M -not -path "$git_root/.git/*" | sed "s|^$git_root/||g")

    # If no large_files, exit
    if [ -z "$large_files" ]; then
        echo "No large files found. Nothing added to .gitignore."
        return
    fi

    # .gitignore path
    gitignore_file="$git_root/.gitignore"

    # Loop through large_files to see if they are already being ignored
    ignored_files=""
    while IFS= read -r file; do
        if ! git check-ignore "$git_root/$file" &> /dev/null; then
            ignored_files="${ignored_files}${file}\n"
        fi
    done <<< "$large_files"

    # If no ignored_files, exit
    if [ -z "$ignored_files" ]; then
        echo "No new large files found. Nothing added to .gitignore."
        return
    fi

    # Remove last \n from list by stripping last two characters
    ignored_files="${ignored_files::-2}"

    # Append new entries to .gitignore
    # -e allows for interpretation of '\n'
    echo -e "$ignored_files" >> "$gitignore_file"
    echo "The following large files have been added to .gitignore:"
    # Print file with tab at beginning
    echo -e "$ignored_files" | sed 's/^/\t/'
}

# only add alias if command does not exsist
if command -v gig &> /dev/null; then
    echo "Error: the 'gig' command already exsists. Did not overwrite with custom command."
else
    alias gig="custom_git_ignore"
fi

#######################################
# update/upgrade/autoremove/autoclean #
#######################################
# only add alias if command does not exsist
if command -v update &> /dev/null; then
    echo "Error: the 'update' command already exsists. Did not overwrite with custom command."
else
    alias update="sudo apt update && sudo apt upgrade && sudo apt autoremove && sudo apt autoclean"
fi

####################
# check gpu status #
####################
# only add alias if command does not exsist
if command -v gpu &> /dev/null; then
    echo "Error: the 'gpu' command already exsists. Did not overwrite with custom command."
else
    alias gpu="conda activate test_gpu && python ~/Software/misc/gpu.py && conda deactivate"
fi

##################################
# open vs code and exit terminal #
##################################
# only add alias if command does not exsist
if command -v codee &> /dev/null; then
    echo "Error: the 'codee' command already exsists. Did not overwrite with custom command."
else
    alias codee="code . ; exit"
fi

#####################################
# update rclone onedrive config PAT #
#####################################
# TODO: close chrome window/tab after opening, 2 clicks + if 2 clicks fails (ie need to log in first) default to wait until Enter is pressed
custom_update_onedrive() {
	# Open Microsoft Graph Explorer
	google-chrome https://developer.microsoft.com/en-us/graph/graph-explorer &> /dev/null

	# # 2 clicks --> WIP
	# # Get mouse id for xinput
	# MOUSE_NAME=$(xinput list --name-only | grep -i mouse | head -n 1)
	# MOUSE_ID=$(xinput list --id-only "$MOUSE_NAME")
	# # Wait for 2 clicks
	# CLICK_COUNT=0
	# xinput test "$MOUSE_ID" | while read -r line; do
	#     if [[ "$line" == "button press   1" ]]; then
	#         ((CLICK_COUNT++))
	#         if [[ $CLICK_COUNT -eq 2 ]]; then
	#             pkill -P $$ xinput  # stop the background listener
	#             break
	#         fi
	#     fi
	# done
	# NEW_PAT=$(xclip -o)
	# echo NEW_PAT

	# Wait until PAT has been copied
	read -p "Copy PAT then press Enter..."

	# Store PAT from clipboard
	NEW_PAT=$(xclip -o)

	# Update rclone config with new PAT
	rclone config update onedrive token "{\"access_token\":\"$NEW_PAT\"}" > /dev/null

	# Check if update was successful
	if rclone lsd onedrive: &> /dev/null; then
	    echo "rclone update successful!"
	else
	    echo "Error: rclone update unsuccessful (OneDrive access failed)."
	fi
}

# only add alias if command does not exsist
if command -v pat &> /dev/null; then
    echo "Error: the 'pat' command already exsists. Did not overwrite with custom command."
else
    alias pat="custom_update_onedrive"
fi
