if [ "$1" = "base" ]; then
  export DOCKER_IMAGE=hoofpilot-base
  export DOCKER_FILE=Dockerfile.hoofpilot_base
elif [ "$1" = "prebuilt" ]; then
  export DOCKER_IMAGE=hoofpilot-prebuilt
  export DOCKER_FILE=Dockerfile.hoofpilot
else
  echo "Invalid docker build image: '$1'"
  exit 1
fi

export DOCKER_REGISTRY=ghcr.io/hoofpilot
export COMMIT_SHA=$(git rev-parse HEAD)

TAG_SUFFIX=$2
LOCAL_TAG=$DOCKER_IMAGE$TAG_SUFFIX
REMOTE_TAG=$DOCKER_REGISTRY/$LOCAL_TAG
REMOTE_SHA_TAG=$DOCKER_REGISTRY/$LOCAL_TAG:$COMMIT_SHA
