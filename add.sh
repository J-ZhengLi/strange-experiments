#!/usr/bin/env bash

set -u

lang='rust'
name=''

is_tool_args=false

par_dir=$(dirname "$0")

cargo_new() {
    # Make sure to create project in the same directory as this script
    cd $par_dir
    cargo new $name $@
}

python_new() {
    local proj_dir=$par_dir/$name
    mkdir $proj_dir
    touch $proj_dir/main.py
    # Write some template code
    echo "#!/usr/bin/env python3

def main():
    print('Hello World!')


if __name__ == '__main__':
    main()" > $proj_dir/main.py
}

update_readme() {
    local repo_readme="$par_dir/README.md"
    local proj_dir="$par_dir/$name"
    local proj_readme="$proj_dir/README.md"

    if [[ ! -d "$proj_dir" ]]; then
        echo "project $name does not exist, maybe it failed to initialized? Aborting."
        exit 1
    fi

    touch $proj_readme
    echo -e "# $name\n\n## Summary\n" > $proj_readme

    # Update repo readme
    echo -e "\n## [$name](./$name/README.md)" >> $repo_readme
}

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -l|--lang)
            lang="$2"
            shift
            ;;
        --)
            is_tool_args=true
            shift
            break
            ;;
        *)
            # Problematic, but it's fine...
            # It's a backup way to specify name for other languages,
            # which is not implemented anyway.
            if [[ -z $name ]]; then
                name="$1"
            elif [[ $is_tool_args == false ]]; then
                echo "Unknown argument: $1"
                exit 1
            fi
            ;;
    esac
    shift
done

if [[ -z $name ]]; then
    echo "no name provided, aborting."
    exit 1
fi

case `echo "$lang" | tr '[:upper:]' '[:lower:]'` in
    'rust')
        cargo_new $@
        ;;
    'python')
        python_new
        ;;
    *)
        echo "unimplemented!"
        exit 1
        ;;
esac

if [[ "$?" == 0 ]]; then
    update_readme
fi
