
function openPreTable(obj, tableName) {
  openTable(obj, tableName, "pTabContent", "pTabLinks")
}

function openRawTable(obj, tableName) {
  openTable(obj, tableName, "rTabContent", "rTabLinks")
}

const options = {};
const smilesDrawer = new SmilesDrawer.Drawer(options);

function openTable(obj, tableName, contentClass, tabLinksClass) {

  let i, tabContent, tabLinks;
  tabContent = document.getElementsByClassName(contentClass);
  for (i = 0; i < tabContent.length; i++) {
    tabContent[i].style.display = "none";
  }
  tabLinks = document.getElementsByClassName(tabLinksClass);
  for (i = 0; i < tabLinks.length; i++) {
    tabLinks[i].className = tabLinks[i].className.replace(" active", "");
  }
  let tableEle = document.getElementById(tableName);
  tableEle.style.display = "block";
  const canvasEleList = tableEle.getElementsByClassName('smiles-canvas')
  for (let i = 0; i < canvasEleList.length; i++) {
    const canvasEle = canvasEleList[i];
    draw(canvasEle.innerHTML, canvasEle.id);
      canvasEle.setAttribute("style", "width:100%");
  }

  obj.className += " active";
}

function draw(input, canvasId) {
  // let t = performance.now();

  SmilesDrawer.parse(input, function (tree) {
    smilesDrawer.draw(tree, canvasId, 'light', false);
  }, function (err) {
    console.log(err);
  });
}

function addCanvas() {
  let smilesEleList, i;
  smilesEleList = document.getElementsByClassName('cleaned-smiles');
  let canvasEleList = new Array();
  for (i = 0; i <smilesEleList.length; i++) {
    const canvasEle = document.createElement('canvas');
    const smilesEle = smilesEleList[i];
    canvasEle.id = 'output-canvas-' + i;
    canvasEle.className = 'smiles-canvas'
    canvasEle.innerHTML = smilesEle.innerText;
    smilesEle.appendChild(canvasEle);
    canvasEleList.push(canvasEle);
  }
  return canvasEleList
}

function drawSmiles() {
  // add canvas
  let canvasEleList = addCanvas()
  for (let i = 0; i < canvasEleList.length; i++) {
    const canvasEle = canvasEleList[i];
    draw(canvasEle.innerHTML, canvasEle.id);
      canvasEle.setAttribute("style", "width:100%");
  }
}