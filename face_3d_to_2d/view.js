
var container;
var camera, scene, renderer;

window.onload = function () {
    init();
    animate();
};
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};
function rotateAroundWorldAxis(object, axis, radians) {
    let rotWorldMatrix = new THREE.Matrix4();
    rotWorldMatrix.makeRotationAxis(axis.normalize(), radians);
    rotWorldMatrix.multiply(object.matrix); 
    object.matrix = rotWorldMatrix; 
    object.rotation.setFromRotationMatrix(object.matrix);
}
function init() {
    var container = document.getElementById('viewer_frame');
    camera = new THREE.OrthographicCamera(-96, 96, -96, 96, 1, 1000);
    camera.up.set(0, 1, 0);
    camera.position.x = 0;
    camera.position.y = 0;
    camera.position.z = 75;
    camera.zoom = 1;
    camera.updateProjectionMatrix();

    scene = new THREE.Scene();
    scene.position.z = 0;
    scene.position.y = 0;

    var manager = new THREE.LoadingManager();
    manager.onProgress = function (item, loaded, total) {
    };

    var onProgress = function (xhr) {
        if (xhr.lengthComputable) {
            var percentComplete = Math.round(xhr.loaded / xhr.total * 100);
            if (percentComplete < 100)
                document.getElementById('progressin').style.width = (percentComplete + '%');
            else {
                var p = document.getElementById('progress');
                p.parentNode.removeChild(p);
            }
        }
    };
    var loader = new THREE.OBJVertexColorLoader(manager);
    loader.load('obj/' + getUrlParameter('id'), function (object) {
        object.children[0].material.side = THREE.DoubleSide;
        object.translateX(-96);
        object.translateY(-96);
        object.translateZ(-30);
        scene.add(object);
        /*var p = document.getElementById('progress');
        p.parentNode.removeChild(p);*/
        
        /*console.log("完成載入");*/
    }, onProgress, function () { });

    let xAxis = new THREE.Vector3(1, 0, 0);
    let yAxis = new THREE.Vector3(0, 1, 0);
    //模型、旋转轴和旋转角度（弧度）
    rotateAroundWorldAxis(scene, xAxis, Math.PI / (180 / getUrlParameter('pitch')));
    rotateAroundWorldAxis(scene, yAxis, Math.PI / (180 / getUrlParameter('yaw')));

    renderer = new THREE.WebGLRenderer({ alpha: true });
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setSize(462, 462);
    container.appendChild(renderer.domElement);
    controls = new THREE.OrbitControls(camera, renderer.domElement);
    
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
