var links = $$('li>a'),
html_map = {},
zz=0,ln=links.length,link,
iframe = document.createElement('iframe'),
attribute_map = {},
result_map = {},
onload,
active_attributes = undefined;

document.body.appendChild(iframe);

window.next = function () {
    var name;
    if (zz > ln-1) {
        return;
    } 
    link = links[zz++];
    name = link.href.split('#')[0];
    if (!html_map[name]) {
        console.log(name);
        html_map[name] = true;
        console.error(link);
        console.error(link.querySelector('.toc-section-name > .element'));
        active_attributes = result_map[link.querySelector('.toc-section-name > .element').innerText] = {
            attributes : {}
        };
        active_attributes = active_attributes.attributes;
        parse_attributes(name,next)
        //iframe.onload = function () {};
        //iframe.src = link;
    } else {
        next();
    }
};


function parse_attributes (href,callback) {
    var 
    attributes,
    aa = 0,
    aln = 0;
    iframe.onload = function () {
        attributes = iframe.contentDocument.querySelectorAll('.attribute-name');
        aa = 0;
        aln = attributes.length;
        next_attribute();
    };
    iframe.src = href;

    function next_attribute () {
        var i,ln;
        var attribute = attributes[aa++];
        if (attribute) {
            if (attribute.tagName === 'A') {
                attrs = attribute_map[attribute.innerText];
                if (attrs) {
                    for (i=0,ln=attrs.length;i<ln;i++) {
                        active_attributes[attrs[i]] = {};
                    }
                    next_attribute();
                }  else {
                    parse_attributes(attribute.href,next_attribute);
                }
            } else {
                active_attributes[attribute.innerText] = {};
                next_attribute();
            }
        } else {
            callback && callback();
        }
    }
}

