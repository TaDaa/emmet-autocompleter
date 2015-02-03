var links = $$('li a'),

html_map = {},
zz=0,ln=links.length,link,
iframe =  document.createElement('iframe'),
result_map = {};
document.body.appendChild(iframe)

iframe.addEventListener('load',function () {if (zz > 0) {
        parse();
        console.log(zz,ln);
        next();
    }
});


window.next = function next () {
    if (zz > ln-1) {
        return;
    }
    link = links[zz++].href.split('#')[0];
    if (!html_map[link]) {
        console.log(link);
        html_map[link] = true ;
        iframe.src = link;
    } else {
        next();
    }
}

function parse() {
    var doc = iframe.contentDocument,
    elements = doc.querySelectorAll('.element-summary'),
    name,attrs,i,ln,attributes,j,jln;
    for (i=0,ln=elements.length;i<ln;i++) {
        element = elements[i];
        name = element.querySelector('.element-name').innerText.replace(/\‘|\’/g,'');
        attrs = Array.prototype.map.call(element.querySelectorAll('.attr-name'),function (d) {return d.innerText.replace(/\‘|\’/g,'')});
        if (result_map[name]) {
            console.error('bad ' + name);
        } else {
            result_map[name] = {
                attributes : {}
            };
            attributes = result_map[name].attributes;
            for (j=0,jln=attrs.length;j<jln;j++) {
                attributes[attrs[j]] = {
                };
            }
        }

    }
}
