const smileDrawerOptions = {
  debug: false,
  atomVisualization: 'default'
};

const smilesDrawer = new SmilesDrawer.Drawer(smileDrawerOptions);

function addCanvas() {
  let smilesEleList, i;
  smilesEleList = document.getElementsByClassName('cleaned-smiles');
  let canvasEleList = new Array();
  for (i = 0; i <smilesEleList.length; i++) {
    const canvasEle = document.createElement('canvas');
    const canvasDivEle = document.createElement('div');
    const smilesEle = smilesEleList[i];
    canvasEle.id = 'output-canvas-' + i;
    canvasEle.className = 'smiles-canvas'
    canvasEle.innerHTML = smilesEle.innerText;
    canvasDivEle.appendChild(canvasEle)
    smilesEle.appendChild(canvasDivEle);
    canvasEleList.push(canvasEle);
  }
  return canvasEleList
}

function doDrawSmiles(input, canvasId) {
    SmilesDrawer.parse(input, function (tree) {
    smilesDrawer.draw(tree, canvasId, 'light', false);
    }, function (err) {
        console.log(err);
    });
}

function drawAllResultSmiles() {
  // add canvas
  let canvasEleList = addCanvas()
  for (let i = 0; i < canvasEleList.length; i++) {
    const canvasEle = canvasEleList[i];
    doDrawSmiles(canvasEle.innerHTML, canvasEle.id);
    canvasEle.setAttribute("style", "width:60%");
  }
}