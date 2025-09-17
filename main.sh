#!/opt/homebrew/bin/zsh -f
# A script for cropping screenshots taken during Discord video calls

readonly SCRIPT_NAME=${0:t2:r}

readonly SCREENSHOT_EXT=png

export -Ua path
path=("${0:A:h}" ${==path})

export -TU PYTHONPATH pythonpath
pythonpath=("${0:A:h}" ${==pythonpath})

show_usage () {
    echo "usage: ${SCRIPT_NAME} [-v | --verbose, -h | --help ] [directory]" 1>&2
}

error_on_invalid_option () {
    echo "${SCRIPT_NAME}: invalid option -- $1" 1>&2
    show_usage
    exit 1
}

################################################################################

while (($#)); do
    case $1 in
        -h | --help   ) show_usage; exit
        ;;
        -v | --verbose) integer -r is_verbose=1
        ;;
        -* | --*      ) error_on_invalid_option $1
        ;;
        *             ) if [[ -d $1 ]]; then cd $1; break
                        else error_on_invalid_option $1
                        fi
        ;;
    esac
    shift
done

setopt EXTENDED_GLOB
readonly orig_filename_pattern="<-99><-12><-31>_<-23><-59><-59>[^[:digit:]]#<-99>#.${SCREENSHOT_EXT}(.N)"
declare -Ua screenshot_files
readonly screenshot_files=(${~orig_filename_pattern})
if ((${#screenshot_files} == 0)); then
    echo "No screenshots to process: ${PWD}" 1>&2
    exit 2
fi

for img in ${==screenshot_files}; do
  new_img=$(main.py "$img")
  exiftool -tagsFromFile "$img" '-all<all'\
    '-MaxAvailWidth<ImageWidth' '-MaxAvailHeight<ImageHeight' "$new_img"
done

# patterns that will be used by `tar` and `rm`
readonly new_filename_subpattern=_new.${SCREENSHOT_EXT}_original
readonly new_filename_pattern=${orig_filename_pattern/".${SCREENSHOT_EXT}"/"${new_filename_subpattern}"}

tar -czf "originals.tar.gz" -v --options gzip:compression-level=1\
  ${==screenshot_files} ${~new_filename_pattern}

rm ${==screenshot_files} ${~new_filename_pattern}

autoload -U zmv
zmv -v '(*)_new.(*)' '$1.$2'