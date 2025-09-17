#!/opt/homebrew/bin/zsh -f
# A script for cropping screenshots taken during Discord video calls

readonly SCRIPT_DIR=${0:A:h}
readonly TARGET_DIR=${1:A}

readonly SCREENSHOT_EXT=png

export -Ua path
path=("$SCRIPT_DIR" ${==path})

export -TU PYTHONPATH pythonpath
pythonpath=("$SCRIPT_DIR" ${==pythonpath})

################################################################################

cd "$TARGET_DIR" || exit 1

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