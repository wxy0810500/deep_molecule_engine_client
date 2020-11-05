const smileDrawerOptions = {
  debug: false,
  atomVisualization: 'default'
};

const smilesDrawer = new SmilesDrawer.Drawer(smileDrawerOptions);

function drawSmiles(input, canvasId) {
    SmilesDrawer.parse(input, function (tree) {
    smilesDrawer.draw(tree, canvasId, 'light', false);
    }, function (err) {
        console.log(err);
    });
    const canvas = document.getElementById(canvasId)
    canvas.setAttribute("style", "width: 48%;")
    return canvas
}

const smilesImagesInstances = []


function drawRadarAndSmiles(input, canvasId, radarDivId, indicatorAndValueDict, dataName) {

    const canvas = drawSmiles(input, canvasId)
    const radarDiv = document.getElementById(radarDivId);
    radarDiv.style.height = canvas.offsetHeight + 'px';
    radarDiv.style.width = canvas.offsetWidth +'px';
    const radarEchart = echarts.init(radarDiv);
    const indicators = []
    const value = []
    for(let indicatorName in indicatorAndValueDict) {
        indicators.push({
            "name": indicatorName,
            "max": 1.0
        })
        value.push(indicatorAndValueDict[indicatorName])
    }


    // 指定图表的配置项和数据
    const radarOptions = {
        tooltip: {
                confine: true,
                enterable: true

        },
        radar: {
            shape: 'polygon',//default
            splitNumber: 5, // 雷达图数设置,default:5
            name: {
                textStyle: {
                    color: 'black',
                    borderRadius: 3,
                    padding: [3, 5]
                }
            },
            indicator : indicators,
            splitArea: {
                areaStyle: {
                    color:  ['#FFF','#D0E4F5']
                }
            }
        },
        series: [{
            name: 's-radar',
            type: 'radar',
            areaStyle: {normal: {opacity: 0}},
            lineStyle: {
                color: "#1C6EA4",
                width: 2

            },
            itemStyle: {
                color: "#1C6EA4"

            },
            data: [
                {name: dataName, value: value}
            ],
        }]
    };

    // 使用刚指定的配置项和数据显示图表。
    radarEchart.setOption(radarOptions);
    smilesImagesInstances.push({
        radarDiv: radarDiv,
        radarEchart: radarEchart,
        canvas: canvas
    })

}

function resizeRadar() {
    for (let smilesImage of smilesImagesInstances) {
        // print(smilesImage)
        let radarEchart = smilesImage.radarEchart
        let canvas = smilesImage.canvas
        let radarDiv = smilesImage.radarDiv
        radarDiv.style.width = canvas.offsetWidth + "px"
        radarDiv.style.height = canvas.offsetHeight + "px"
        radarEchart.resize()
    }
}

window.addEventListener('resize', resizeRadar)