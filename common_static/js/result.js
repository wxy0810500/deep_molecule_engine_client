function openPreTable(obj, tableName) {
  openTable(obj, tableName, "pTabContent", "pTabLinks")
}

function openRawTable(obj, tableName) {
  openTable(obj, tableName, "rTabContent", "rTabLinks")
}


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
  document.getElementById(tableName).style.display = "block";
  obj.className += " active";
}


var options = {
  debug: false,
  atomVisualization: 'default'
}

var smilesDrawer = new SmilesDrawer.Drawer(options);

function draw(input, canvasId) {
  // let t = performance.now();

  SmilesDrawer.parse(input, canvasId, function (tree) {
    smilesDrawer.draw(tree, canvasId, 'light', false);
    // let td = performance.now() - t;
    /*log.innerHTML = '&nbsp;';
    log.style.visibility = 'hidden';

    new Noty({
      text: 'Drawing took ' + td.toFixed(3) + 'ms with a total overlap score of ' + smilesDrawer.getTotalOverlapScore().toFixed(3) + '.',
      killer: true,
      timeout: 2000,
      animation: {
        open: null,
        close: null
      }
    }).show();*/
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