const options = {
  debug: false,
  atomVisualization: 'default'
};

const smilesDrawer = new SmilesDrawer.Drawer(options);

function draw(input, canvasId) {
  // let t = performance.now();

  SmilesDrawer.parse(input, canvasId, function (tree) {
    smilesDrawer.draw(tree, canvasId, 'light', false);
  }, function (err) {
    // log.innerHTML = err;
    // log.style.visibility = 'visible';
    console.log(err);
  });
}


function drawSmiles() {
  // add canvas
  let smilesEle, i;
  smilesEle = document.getElementsByClassName('cleaned-smiles');

  for (i = 0; i <smilesEle.length; i++) {
    var canvasEls = document.createElement('canvas')
    canvasEls.id = 'output-canvas-' + i
    draw(smilesEle.value, canvasEls.id)
  }

}