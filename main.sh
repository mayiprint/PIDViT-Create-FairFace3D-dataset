#! /bin/bash
# by Chia-Hsin Tsai
# Ubuntu 18.04

# 輸出顏色文字
red(){
    echo -e "\033[31m\033[01m$1\033[0m"
}
green(){
    echo -e "\033[32m\033[01m$1\033[0m"
}
blue(){
    echo -e "\033[34m\033[01m$1\033[0m"
}

# 安装Docker
function docker-install(){
    echo "Check for Docker Installation……"
    docker -v
    if [ $? -ne  0 ]; then
        echo " ***** Install Docker ***** "
        curl -sL get.docker.com|bash
        systemctl start docker
        systemctl enable docker
        echo " ***** Install Docker complete ***** "
    fi
}

# 下載fairface資料集
function download-fairface(){
    mkdir dataset
    wget --save-cookies cookies.txt 'https://docs.google.com/uc?export=download&id=1Z1RqRo0_JiavaZw2yzZG6WETdZQ8qX86' -O- \
        | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p' > confirm.txt
    wget --load-cookies cookies.txt -O 'dataset/fairface-img-margin025-trainval.zip' \
        'https://docs.google.com/uc?export=download&id=1Z1RqRo0_JiavaZw2yzZG6WETdZQ8qX86&confirm='$(<confirm.txt)
    rm confirm.txt
    rm cookies.txt
    rm -rf dataset/fairface-img-margin025-trainval
    unzip dataset/fairface-img-margin025-trainval.zip -d dataset/fairface-img-margin025-trainval
    rm -f dataset/fairface-img-margin025-trainval.zip
}

# 下載fairface測試樣本
function download-fairface-demo(){
    mkdir dataset
    wget --save-cookies cookies.txt 'https://docs.google.com/uc?export=download&id=1WkyWwbCxlPONQdEv8w6Z1MKKVR_dcVsE' -O- \
        | sed -rn 's/.*confirm=([0-9A-Za-z_]+).*/\1/p' > confirm.txt
    wget --load-cookies cookies.txt -O 'dataset/fairface-demo.tar' \
        'https://docs.google.com/uc?export=download&id=1WkyWwbCxlPONQdEv8w6Z1MKKVR_dcVsE&confirm='$(<confirm.txt)
    rm confirm.txt
    rm cookies.txt
    rm -rf dataset/fairface-img-margin025-trainval
    mkdir dataset/fairface-img-margin025-trainval
    tar xvf dataset/fairface-demo.tar  -C dataset/fairface-img-margin025-trainval/
    rm -f dataset/fairface-demo.tar
}

function create-2d-face(){
    ABSPATH=$(readlink -f "$0")
    SCRIPTPATH=$(dirname "$ABSPATH")
    cp -r $SCRIPTPATH/dataset/fairface-3d/tmp/obj $SCRIPTPATH/face_3d_to_2d/obj
    green "Can't be done with bash shell, need to do it manually"
    green "Use the Ubuntu desktop version"
    green "Download chromedriver according to the chrome version to $SCRIPTPATH/face_3d_to_2d"
    echo "cd '$SCRIPTPATH/face_3d_to_2d'"
    echo "pip3 install -r requirements.txt"
    echo "python3 generate_face_images.py"
}

# 產生3D人臉重建模型
function create-3d-face(){
    ABSPATH=$(readlink -f "$0")
    SCRIPTPATH=$(dirname "$ABSPATH")
    if [[ "$(docker images -q vrn-cpu 2> /dev/null)" == "" ]]; then
        # 建立人臉重建Docker Images
        cd docker_3d_face_reconstruction
        docker build -t vrn-cpu . --no-cache
        cd ../
    fi
    docker run --rm -v $SCRIPTPATH:/data --name vrn-cpu vrn-cpu
}

function filter-face(){
    ABSPATH=$(readlink -f "$0")
    SCRIPTPATH=$(dirname "$ABSPATH")
    if [[ "$(docker images -q filter-face 2> /dev/null)" == "" ]]; then
        cd docker_filter_face
        docker build -t filter-face . --no-cache
        cd ../
    fi
    docker run --rm -v $SCRIPTPATH:/data --name filter-face filter-face
}

# 移除Docker Images
function remove-docker-images(){
    if [[ "$(docker images -q vrn-cpu 2> /dev/null)" != "" ]]; then
        docker rm vrn-cpu
        docker rmi vrn-cpu
    fi
    if [[ "$(docker images -q filter-face 2> /dev/null)" != "" ]]; then
        docker rm filter-face
        docker rmi filter-face
    fi
}
function remove-tmp(){
    rm -rf dataset/fairface-3d/tmp
    rm -rf dataset/vrn
    rm -rf face_3d_to_2d/obj
}
# 選單
function start_menu(){
    clear
    blue " Thank you for using the create the FairFace-3D dataset tool."
    echo
    green " Choose a number from below, or type in your own value"
    green " ＝＝＝＝＝＝＝＝＝＝＝ Download Dataset ＝＝＝＝＝＝＝＝＝＝＝＝＝＝"
    green " 1. Download the fairface Dataset"
    green " 2. Download the fairface 10 Samples (Test Run Only)"
    green " ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝"
    echo 
    green " ＝＝＝＝＝＝＝＝＝ Creat FairFace-3D Dataset Tool ＝＝＝＝＝＝＝＝＝"
    green " 3. Install Docker on Linux"
    green " 4. Perform 3D Face Reconstruction (CPU)"
    green " 5. 3D Model to 2D Face Image"
    green " 6. Filter Out Abnormal Face (CPU)"
    green " ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝"
    echo
    green " ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝ Remove ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝"
    green " 8. Remove FairFace-3D Temporary Files"
    green " 9. Remove Docker Images"
    green " ＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝"
    green " 0. Exit"
    echo
    read -p "scope> " menuNumberInput
    case "$menuNumberInput" in
        1 )
           download-fairface
	    ;;
        2)
           download-fairface-demo
	    ;;
        3 )
           docker-install
        ;;
        4 )
           create-3d-face
        ;;
        5 )
           create-2d-face
        ;;
        6 )
           filter-face
        ;;
        8 )
           remove-tmp
        ;;
        9 )
           remove-docker-images
        ;;
        0 )
            exit 1
            start_menu
        ;;
        * )
            clear
            red "Please enter the correct number!"
            start_menu
        ;;
    esac
}
start_menu "first"