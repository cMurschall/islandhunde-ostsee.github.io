/* eslint-disable */

let uuidCounter = 0;
const generateUniqueId = () => {
    uuidCounter++;
    return "pedigreeChartId" + uuidCounter;
};

const renderDogPedigreeChart = (containerId, dogData) => {
    const pedigreeId = generateUniqueId();

    const containerElement = document.getElementById(containerId);
    if (!containerElement) {
        console.error(`Container-Element mit ID '${containerId}' nicht gefunden.`);
        return;
    }

    const innerDiv = document.createElement('div');
    innerDiv.id = pedigreeId;
    innerDiv.className = 'pedigree';
    containerElement.appendChild(innerDiv);

    const aspectRatio = 1 / 2;
    const generationDepth = 2; // Annahme: Passe dies an die tatsächliche Generationstiefe deiner Daten an

    const imageWidth = generationDepth * 410;
    const imageHeight = imageWidth * aspectRatio;
    const textSize = 18;

    const boxWidth = imageWidth / (generationDepth + 1);
    const boxHeight = boxWidth * 0.6;

    const flagheight = textSize * 1.28;
    const flagwidth = (flagheight * 3) / 4;


    const getOrigin = dog => {
        const origin = dog.id.substring(0, 2).toLowerCase();
        return origin ?? "is"; // Standardmäßig Island, falls kein Ursprung angegeben ist
    };
    // ----------------------

    const isLeaf = dog => {
        return dog.parents === undefined || dog.parents.length === 0;
    };

    const isRoot = dog => {
        return dog.isRoot;
    };

    const elbow = d => {
        let start = d.source.y;
        let end = d.target.y;

        if (isRoot(d.source.data)) {
            start = d.source.y - boxWidth / 2.3;
        } else if (isLeaf(d.target.data)) {
            end = d.target.y + boxWidth / 2.3;
        }

        return `M${start},${d.source.x}H${d.source.y +
            (d.target.y - d.source.y) / 2}V${d.target.x}H${end}`;
    };

    const svg = d3
        .select("#" + pedigreeId)
        .append("svg")
        .attr("viewBox", `0 0 ${imageWidth} ${imageHeight}`)
        .attr("preserveAspectRatio", "xMinYMin meet")
        .append("g")
        .attr("transform", `translate(${boxWidth * 0.5},${imageHeight / 2})`);

    const nodes = d3.hierarchy(dogData, d => d.parents);

    const tree = d3
        .tree()
        .nodeSize([boxHeight, boxWidth])
        .separation((a, b) => {
            return (a.parent === b.parent) ? 0.7 : 0.5;
        });

    const treeNodes = tree(nodes);

    const link = svg
        .selectAll("path.link")
        .data(nodes.links())
        .enter()
        .append("path")
        .attr("class", "link")
        .attr("d", elbow);

    const node = svg
        .selectAll("g.dog")
        .data(treeNodes.descendants())
        .enter()
        .append("g")
        .attr("class", "dog")
        .attr("transform", d => {
            return `translate(${d.y},${d.x})`;
        });

    node
        .append("text")
        .attr("x", -(boxWidth / 2.3 - flagwidth * 1.15))
        .attr("y", -flagheight * 0.25)
        .attr("text-anchor", "start")
        .attr("style", `font-size:${textSize}px`)
        .attr("class", "name")
        .text(d => {
            return d.data.name_and_origin;
        });

    node
        .append("image")
        .attr("x", -(boxWidth / 2.3))
        .attr("y", -flagheight)
        .attr("height", flagheight)
        .attr("width", flagwidth)
        .attr("xlink:href", d => {
            // Hier wird immer die Island-Flagge verwendet
            return `https://raw.githubusercontent.com/lipis/flag-icons/refs/heads/main/flags/4x3/${getOrigin(d.data)}.svg`;
        });

    node
        .append("text")
        .attr("dx", -(boxWidth / 2.3))
        .attr("dy", flagheight * 0.8)
        .attr("text-anchor", "start")
        .attr("style", `font-size:${textSize}px`)
        .attr("class", "id")
        .text(d => (isRoot(d.data) ? "" : d.data.id));

    node
        .append("text")
        .attr("dx", -(boxWidth / 2.3))
        .attr("dy", flagheight * 0.8 + textSize * 1.2) // etwas unterhalb der ID
        .attr("text-anchor", "start")
        .attr("style", `font-size:${textSize * 0.9}px; fill: #555`) // etwas kleiner und dunkler
        .attr("class", "hd")
        .text(d => d.data.hd ? `HD: ${d.data.hd}` : "");
};

window.renderDogPedigreeChart = renderDogPedigreeChart;