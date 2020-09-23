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