import{c2 as Ze,R as ee,k as t,d as X,g as le,$ as ke,bS as St,c as kt,bx as Pt,S as U,b as p,bu as $e,aZ as Lt,M as Tt,V as N,r as V,a0 as Ot,ag as xe,aj as fe,am as Xe,a1 as re,e as T,u as de,j as Pe,bg as Bt,c3 as It,p as ze,c4 as $t,ar as ye,Q as Ce,Y as H,v as zt,q as Dt,aY as Mt,ap as Re,a9 as Le,a7 as _t,F as De,a8 as Se,O as $,f as ne,c5 as qe,c6 as Ye,bX as Ge,c7 as Ke,c8 as Ut,h as Me,bo as ve,i as jt,X as Et,c9 as Je,a6 as Ft,E as ge,W as At,as as Nt,ca as _e,N as Q,T as Ht,cb as Wt,a5 as Vt,a4 as Zt,cc as Xt,af as qt,ai as Ue}from"./index.eb4377b0.1766986584207.js";import{A as Yt}from"./Add.3491e10c.1766986584207.js";import{o as Gt,i as Kt}from"./utils.83ed917f.1766986584207.js";import{u as Jt,E as Qt}from"./Eye.1e3444f4.1766986584207.js";import{N as er}from"./Tooltip.2d4fe76d.1766986584207.js";function tr(e,o,r,i){var n=-1,s=e==null?0:e.length;for(i&&s&&(r=e[++n]);++n<s;)r=o(r,e[n],n,e);return r}function rr(e){return function(o){return e==null?void 0:e[o]}}var or={\u00C0:"A",\u00C1:"A",\u00C2:"A",\u00C3:"A",\u00C4:"A",\u00C5:"A",\u00E0:"a",\u00E1:"a",\u00E2:"a",\u00E3:"a",\u00E4:"a",\u00E5:"a",\u00C7:"C",\u00E7:"c",\u00D0:"D",\u00F0:"d",\u00C8:"E",\u00C9:"E",\u00CA:"E",\u00CB:"E",\u00E8:"e",\u00E9:"e",\u00EA:"e",\u00EB:"e",\u00CC:"I",\u00CD:"I",\u00CE:"I",\u00CF:"I",\u00EC:"i",\u00ED:"i",\u00EE:"i",\u00EF:"i",\u00D1:"N",\u00F1:"n",\u00D2:"O",\u00D3:"O",\u00D4:"O",\u00D5:"O",\u00D6:"O",\u00D8:"O",\u00F2:"o",\u00F3:"o",\u00F4:"o",\u00F5:"o",\u00F6:"o",\u00F8:"o",\u00D9:"U",\u00DA:"U",\u00DB:"U",\u00DC:"U",\u00F9:"u",\u00FA:"u",\u00FB:"u",\u00FC:"u",\u00DD:"Y",\u00FD:"y",\u00FF:"y",\u00C6:"Ae",\u00E6:"ae",\u00DE:"Th",\u00FE:"th",\u00DF:"ss",\u0100:"A",\u0102:"A",\u0104:"A",\u0101:"a",\u0103:"a",\u0105:"a",\u0106:"C",\u0108:"C",\u010A:"C",\u010C:"C",\u0107:"c",\u0109:"c",\u010B:"c",\u010D:"c",\u010E:"D",\u0110:"D",\u010F:"d",\u0111:"d",\u0112:"E",\u0114:"E",\u0116:"E",\u0118:"E",\u011A:"E",\u0113:"e",\u0115:"e",\u0117:"e",\u0119:"e",\u011B:"e",\u011C:"G",\u011E:"G",\u0120:"G",\u0122:"G",\u011D:"g",\u011F:"g",\u0121:"g",\u0123:"g",\u0124:"H",\u0126:"H",\u0125:"h",\u0127:"h",\u0128:"I",\u012A:"I",\u012C:"I",\u012E:"I",\u0130:"I",\u0129:"i",\u012B:"i",\u012D:"i",\u012F:"i",\u0131:"i",\u0134:"J",\u0135:"j",\u0136:"K",\u0137:"k",\u0138:"k",\u0139:"L",\u013B:"L",\u013D:"L",\u013F:"L",\u0141:"L",\u013A:"l",\u013C:"l",\u013E:"l",\u0140:"l",\u0142:"l",\u0143:"N",\u0145:"N",\u0147:"N",\u014A:"N",\u0144:"n",\u0146:"n",\u0148:"n",\u014B:"n",\u014C:"O",\u014E:"O",\u0150:"O",\u014D:"o",\u014F:"o",\u0151:"o",\u0154:"R",\u0156:"R",\u0158:"R",\u0155:"r",\u0157:"r",\u0159:"r",\u015A:"S",\u015C:"S",\u015E:"S",\u0160:"S",\u015B:"s",\u015D:"s",\u015F:"s",\u0161:"s",\u0162:"T",\u0164:"T",\u0166:"T",\u0163:"t",\u0165:"t",\u0167:"t",\u0168:"U",\u016A:"U",\u016C:"U",\u016E:"U",\u0170:"U",\u0172:"U",\u0169:"u",\u016B:"u",\u016D:"u",\u016F:"u",\u0171:"u",\u0173:"u",\u0174:"W",\u0175:"w",\u0176:"Y",\u0177:"y",\u0178:"Y",\u0179:"Z",\u017B:"Z",\u017D:"Z",\u017A:"z",\u017C:"z",\u017E:"z",\u0132:"IJ",\u0133:"ij",\u0152:"Oe",\u0153:"oe",\u0149:"'n",\u017F:"s"},ir=rr(or);const nr=ir;var ar=/[\xc0-\xd6\xd8-\xf6\xf8-\xff\u0100-\u017f]/g,lr="\\u0300-\\u036f",sr="\\ufe20-\\ufe2f",ur="\\u20d0-\\u20ff",dr=lr+sr+ur,cr="["+dr+"]",fr=RegExp(cr,"g");function gr(e){return e=Ze(e),e&&e.replace(ar,nr).replace(fr,"")}var hr=/[^\x00-\x2f\x3a-\x40\x5b-\x60\x7b-\x7f]+/g;function pr(e){return e.match(hr)||[]}var vr=/[a-z][A-Z]|[A-Z]{2}[a-z]|[0-9][a-zA-Z]|[a-zA-Z][0-9]|[^a-zA-Z0-9 ]/;function mr(e){return vr.test(e)}var Qe="\\ud800-\\udfff",br="\\u0300-\\u036f",wr="\\ufe20-\\ufe2f",xr="\\u20d0-\\u20ff",yr=br+wr+xr,et="\\u2700-\\u27bf",tt="a-z\\xdf-\\xf6\\xf8-\\xff",Cr="\\xac\\xb1\\xd7\\xf7",Rr="\\x00-\\x2f\\x3a-\\x40\\x5b-\\x60\\x7b-\\xbf",Sr="\\u2000-\\u206f",kr=" \\t\\x0b\\f\\xa0\\ufeff\\n\\r\\u2028\\u2029\\u1680\\u180e\\u2000\\u2001\\u2002\\u2003\\u2004\\u2005\\u2006\\u2007\\u2008\\u2009\\u200a\\u202f\\u205f\\u3000",rt="A-Z\\xc0-\\xd6\\xd8-\\xde",Pr="\\ufe0e\\ufe0f",ot=Cr+Rr+Sr+kr,it="['\u2019]",je="["+ot+"]",Lr="["+yr+"]",nt="\\d+",Tr="["+et+"]",at="["+tt+"]",lt="[^"+Qe+ot+nt+et+tt+rt+"]",Or="\\ud83c[\\udffb-\\udfff]",Br="(?:"+Lr+"|"+Or+")",Ir="[^"+Qe+"]",st="(?:\\ud83c[\\udde6-\\uddff]){2}",ut="[\\ud800-\\udbff][\\udc00-\\udfff]",ae="["+rt+"]",$r="\\u200d",Ee="(?:"+at+"|"+lt+")",zr="(?:"+ae+"|"+lt+")",Fe="(?:"+it+"(?:d|ll|m|re|s|t|ve))?",Ae="(?:"+it+"(?:D|LL|M|RE|S|T|VE))?",dt=Br+"?",ct="["+Pr+"]?",Dr="(?:"+$r+"(?:"+[Ir,st,ut].join("|")+")"+ct+dt+")*",Mr="\\d*(?:1st|2nd|3rd|(?![123])\\dth)(?=\\b|[A-Z_])",_r="\\d*(?:1ST|2ND|3RD|(?![123])\\dTH)(?=\\b|[a-z_])",Ur=ct+dt+Dr,jr="(?:"+[Tr,st,ut].join("|")+")"+Ur,Er=RegExp([ae+"?"+at+"+"+Fe+"(?="+[je,ae,"$"].join("|")+")",zr+"+"+Ae+"(?="+[je,ae+Ee,"$"].join("|")+")",ae+"?"+Ee+"+"+Fe,ae+"+"+Ae,_r,Mr,nt,jr].join("|"),"g");function Fr(e){return e.match(Er)||[]}function Ar(e,o,r){return e=Ze(e),o=r?void 0:o,o===void 0?mr(e)?Fr(e):pr(e):e.match(o)||[]}var Nr="['\u2019]",Hr=RegExp(Nr,"g");function Wr(e){return function(o){return tr(Ar(gr(o).replace(Hr,"")),e,"")}}var Vr=Wr(function(e,o,r){return e+(r?"-":"")+o.toLowerCase()});const Zr=Vr,Xr=ee("attach",t("svg",{viewBox:"0 0 16 16",version:"1.1",xmlns:"http://www.w3.org/2000/svg"},t("g",{stroke:"none","stroke-width":"1",fill:"none","fill-rule":"evenodd"},t("g",{fill:"currentColor","fill-rule":"nonzero"},t("path",{d:"M3.25735931,8.70710678 L7.85355339,4.1109127 C8.82986412,3.13460197 10.4127766,3.13460197 11.3890873,4.1109127 C12.365398,5.08722343 12.365398,6.67013588 11.3890873,7.64644661 L6.08578644,12.9497475 C5.69526215,13.3402718 5.06209717,13.3402718 4.67157288,12.9497475 C4.28104858,12.5592232 4.28104858,11.9260582 4.67157288,11.5355339 L9.97487373,6.23223305 C10.1701359,6.0369709 10.1701359,5.72038841 9.97487373,5.52512627 C9.77961159,5.32986412 9.4630291,5.32986412 9.26776695,5.52512627 L3.96446609,10.8284271 C3.18341751,11.6094757 3.18341751,12.8758057 3.96446609,13.6568542 C4.74551468,14.4379028 6.01184464,14.4379028 6.79289322,13.6568542 L12.0961941,8.35355339 C13.4630291,6.98671837 13.4630291,4.77064094 12.0961941,3.40380592 C10.7293591,2.0369709 8.51328163,2.0369709 7.14644661,3.40380592 L2.55025253,8 C2.35499039,8.19526215 2.35499039,8.51184464 2.55025253,8.70710678 C2.74551468,8.90236893 3.06209717,8.90236893 3.25735931,8.70710678 Z"}))))),qr=ee("trash",t("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 512 512"},t("path",{d:"M432,144,403.33,419.74A32,32,0,0,1,371.55,448H140.46a32,32,0,0,1-31.78-28.26L80,144",style:"fill: none; stroke: currentcolor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 32px;"}),t("rect",{x:"32",y:"64",width:"448",height:"80",rx:"16",ry:"16",style:"fill: none; stroke: currentcolor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 32px;"}),t("line",{x1:"312",y1:"240",x2:"200",y2:"352",style:"fill: none; stroke: currentcolor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 32px;"}),t("line",{x1:"312",y1:"352",x2:"200",y2:"240",style:"fill: none; stroke: currentcolor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 32px;"}))),Yr=ee("download",t("svg",{viewBox:"0 0 16 16",version:"1.1",xmlns:"http://www.w3.org/2000/svg"},t("g",{stroke:"none","stroke-width":"1",fill:"none","fill-rule":"evenodd"},t("g",{fill:"currentColor","fill-rule":"nonzero"},t("path",{d:"M3.5,13 L12.5,13 C12.7761424,13 13,13.2238576 13,13.5 C13,13.7454599 12.8231248,13.9496084 12.5898756,13.9919443 L12.5,14 L3.5,14 C3.22385763,14 3,13.7761424 3,13.5 C3,13.2545401 3.17687516,13.0503916 3.41012437,13.0080557 L3.5,13 L12.5,13 L3.5,13 Z M7.91012437,1.00805567 L8,1 C8.24545989,1 8.44960837,1.17687516 8.49194433,1.41012437 L8.5,1.5 L8.5,10.292 L11.1819805,7.6109127 C11.3555469,7.43734635 11.6249713,7.4180612 11.8198394,7.55305725 L11.8890873,7.6109127 C12.0626536,7.78447906 12.0819388,8.05390346 11.9469427,8.2487716 L11.8890873,8.31801948 L8.35355339,11.8535534 C8.17998704,12.0271197 7.91056264,12.0464049 7.7156945,11.9114088 L7.64644661,11.8535534 L4.1109127,8.31801948 C3.91565056,8.12275734 3.91565056,7.80617485 4.1109127,7.6109127 C4.28447906,7.43734635 4.55390346,7.4180612 4.7487716,7.55305725 L4.81801948,7.6109127 L7.5,10.292 L7.5,1.5 C7.5,1.25454011 7.67687516,1.05039163 7.91012437,1.00805567 L8,1 L7.91012437,1.00805567 Z"}))))),Gr=ee("cancel",t("svg",{viewBox:"0 0 16 16",version:"1.1",xmlns:"http://www.w3.org/2000/svg"},t("g",{stroke:"none","stroke-width":"1",fill:"none","fill-rule":"evenodd"},t("g",{fill:"currentColor","fill-rule":"nonzero"},t("path",{d:"M2.58859116,2.7156945 L2.64644661,2.64644661 C2.82001296,2.47288026 3.08943736,2.45359511 3.2843055,2.58859116 L3.35355339,2.64644661 L8,7.293 L12.6464466,2.64644661 C12.8417088,2.45118446 13.1582912,2.45118446 13.3535534,2.64644661 C13.5488155,2.84170876 13.5488155,3.15829124 13.3535534,3.35355339 L8.707,8 L13.3535534,12.6464466 C13.5271197,12.820013 13.5464049,13.0894374 13.4114088,13.2843055 L13.3535534,13.3535534 C13.179987,13.5271197 12.9105626,13.5464049 12.7156945,13.4114088 L12.6464466,13.3535534 L8,8.707 L3.35355339,13.3535534 C3.15829124,13.5488155 2.84170876,13.5488155 2.64644661,13.3535534 C2.45118446,13.1582912 2.45118446,12.8417088 2.64644661,12.6464466 L7.293,8 L2.64644661,3.35355339 C2.47288026,3.17998704 2.45359511,2.91056264 2.58859116,2.7156945 L2.64644661,2.64644661 L2.58859116,2.7156945 Z"}))))),Kr=ee("retry",t("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 512 512"},t("path",{d:"M320,146s24.36-12-64-12A160,160,0,1,0,416,294",style:"fill: none; stroke: currentcolor; stroke-linecap: round; stroke-miterlimit: 10; stroke-width: 32px;"}),t("polyline",{points:"256 58 336 138 256 218",style:"fill: none; stroke: currentcolor; stroke-linecap: round; stroke-linejoin: round; stroke-width: 32px;"}))),Jr=ee("rotateClockwise",t("svg",{viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t("path",{d:"M3 10C3 6.13401 6.13401 3 10 3C13.866 3 17 6.13401 17 10C17 12.7916 15.3658 15.2026 13 16.3265V14.5C13 14.2239 12.7761 14 12.5 14C12.2239 14 12 14.2239 12 14.5V17.5C12 17.7761 12.2239 18 12.5 18H15.5C15.7761 18 16 17.7761 16 17.5C16 17.2239 15.7761 17 15.5 17H13.8758C16.3346 15.6357 18 13.0128 18 10C18 5.58172 14.4183 2 10 2C5.58172 2 2 5.58172 2 10C2 10.2761 2.22386 10.5 2.5 10.5C2.77614 10.5 3 10.2761 3 10Z",fill:"currentColor"}),t("path",{d:"M10 12C11.1046 12 12 11.1046 12 10C12 8.89543 11.1046 8 10 8C8.89543 8 8 8.89543 8 10C8 11.1046 8.89543 12 10 12ZM10 11C9.44772 11 9 10.5523 9 10C9 9.44772 9.44772 9 10 9C10.5523 9 11 9.44772 11 10C11 10.5523 10.5523 11 10 11Z",fill:"currentColor"}))),Qr=ee("rotateClockwise",t("svg",{viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t("path",{d:"M17 10C17 6.13401 13.866 3 10 3C6.13401 3 3 6.13401 3 10C3 12.7916 4.63419 15.2026 7 16.3265V14.5C7 14.2239 7.22386 14 7.5 14C7.77614 14 8 14.2239 8 14.5V17.5C8 17.7761 7.77614 18 7.5 18H4.5C4.22386 18 4 17.7761 4 17.5C4 17.2239 4.22386 17 4.5 17H6.12422C3.66539 15.6357 2 13.0128 2 10C2 5.58172 5.58172 2 10 2C14.4183 2 18 5.58172 18 10C18 10.2761 17.7761 10.5 17.5 10.5C17.2239 10.5 17 10.2761 17 10Z",fill:"currentColor"}),t("path",{d:"M10 12C8.89543 12 8 11.1046 8 10C8 8.89543 8.89543 8 10 8C11.1046 8 12 8.89543 12 10C12 11.1046 11.1046 12 10 12ZM10 11C10.5523 11 11 10.5523 11 10C11 9.44772 10.5523 9 10 9C9.44772 9 9 9.44772 9 10C9 10.5523 9.44772 11 10 11Z",fill:"currentColor"}))),eo=ee("zoomIn",t("svg",{viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t("path",{d:"M11.5 8.5C11.5 8.22386 11.2761 8 11 8H9V6C9 5.72386 8.77614 5.5 8.5 5.5C8.22386 5.5 8 5.72386 8 6V8H6C5.72386 8 5.5 8.22386 5.5 8.5C5.5 8.77614 5.72386 9 6 9H8V11C8 11.2761 8.22386 11.5 8.5 11.5C8.77614 11.5 9 11.2761 9 11V9H11C11.2761 9 11.5 8.77614 11.5 8.5Z",fill:"currentColor"}),t("path",{d:"M8.5 3C11.5376 3 14 5.46243 14 8.5C14 9.83879 13.5217 11.0659 12.7266 12.0196L16.8536 16.1464C17.0488 16.3417 17.0488 16.6583 16.8536 16.8536C16.68 17.0271 16.4106 17.0464 16.2157 16.9114L16.1464 16.8536L12.0196 12.7266C11.0659 13.5217 9.83879 14 8.5 14C5.46243 14 3 11.5376 3 8.5C3 5.46243 5.46243 3 8.5 3ZM8.5 4C6.01472 4 4 6.01472 4 8.5C4 10.9853 6.01472 13 8.5 13C10.9853 13 13 10.9853 13 8.5C13 6.01472 10.9853 4 8.5 4Z",fill:"currentColor"}))),to=ee("zoomOut",t("svg",{viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t("path",{d:"M11 8C11.2761 8 11.5 8.22386 11.5 8.5C11.5 8.77614 11.2761 9 11 9H6C5.72386 9 5.5 8.77614 5.5 8.5C5.5 8.22386 5.72386 8 6 8H11Z",fill:"currentColor"}),t("path",{d:"M14 8.5C14 5.46243 11.5376 3 8.5 3C5.46243 3 3 5.46243 3 8.5C3 11.5376 5.46243 14 8.5 14C9.83879 14 11.0659 13.5217 12.0196 12.7266L16.1464 16.8536L16.2157 16.9114C16.4106 17.0464 16.68 17.0271 16.8536 16.8536C17.0488 16.6583 17.0488 16.3417 16.8536 16.1464L12.7266 12.0196C13.5217 11.0659 14 9.83879 14 8.5ZM4 8.5C4 6.01472 6.01472 4 8.5 4C10.9853 4 13 6.01472 13 8.5C13 10.9853 10.9853 13 8.5 13C6.01472 13 4 10.9853 4 8.5Z",fill:"currentColor"}))),ro=X({name:"ResizeSmall",render(){return t("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 20 20"},t("g",{fill:"none"},t("path",{d:"M5.5 4A1.5 1.5 0 0 0 4 5.5v1a.5.5 0 0 1-1 0v-1A2.5 2.5 0 0 1 5.5 3h1a.5.5 0 0 1 0 1h-1zM16 5.5A1.5 1.5 0 0 0 14.5 4h-1a.5.5 0 0 1 0-1h1A2.5 2.5 0 0 1 17 5.5v1a.5.5 0 0 1-1 0v-1zm0 9a1.5 1.5 0 0 1-1.5 1.5h-1a.5.5 0 0 0 0 1h1a2.5 2.5 0 0 0 2.5-2.5v-1a.5.5 0 0 0-1 0v1zm-12 0A1.5 1.5 0 0 0 5.5 16h1.25a.5.5 0 0 1 0 1H5.5A2.5 2.5 0 0 1 3 14.5v-1.25a.5.5 0 0 1 1 0v1.25zM8.5 7A1.5 1.5 0 0 0 7 8.5v3A1.5 1.5 0 0 0 8.5 13h3a1.5 1.5 0 0 0 1.5-1.5v-3A1.5 1.5 0 0 0 11.5 7h-3zM8 8.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 .5.5v3a.5.5 0 0 1-.5.5h-3a.5.5 0 0 1-.5-.5v-3z",fill:"currentColor"})))}}),Te=Object.assign(Object.assign({},le.props),{showToolbar:{type:Boolean,default:!0},showToolbarTooltip:Boolean}),ft=ke("n-image");function oo(){return{toolbarIconColor:"rgba(255, 255, 255, .9)",toolbarColor:"rgba(0, 0, 0, .35)",toolbarBoxShadow:"none",toolbarBorderRadius:"24px"}}const io=St({name:"Image",common:kt,peers:{Tooltip:Pt},self:oo}),no=t("svg",{viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t("path",{d:"M6 5C5.75454 5 5.55039 5.17688 5.50806 5.41012L5.5 5.5V14.5C5.5 14.7761 5.72386 15 6 15C6.24546 15 6.44961 14.8231 6.49194 14.5899L6.5 14.5V5.5C6.5 5.22386 6.27614 5 6 5ZM13.8536 5.14645C13.68 4.97288 13.4106 4.9536 13.2157 5.08859L13.1464 5.14645L8.64645 9.64645C8.47288 9.82001 8.4536 10.0894 8.58859 10.2843L8.64645 10.3536L13.1464 14.8536C13.3417 15.0488 13.6583 15.0488 13.8536 14.8536C14.0271 14.68 14.0464 14.4106 13.9114 14.2157L13.8536 14.1464L9.70711 10L13.8536 5.85355C14.0488 5.65829 14.0488 5.34171 13.8536 5.14645Z",fill:"currentColor"})),ao=t("svg",{viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t("path",{d:"M13.5 5C13.7455 5 13.9496 5.17688 13.9919 5.41012L14 5.5V14.5C14 14.7761 13.7761 15 13.5 15C13.2545 15 13.0504 14.8231 13.0081 14.5899L13 14.5V5.5C13 5.22386 13.2239 5 13.5 5ZM5.64645 5.14645C5.82001 4.97288 6.08944 4.9536 6.28431 5.08859L6.35355 5.14645L10.8536 9.64645C11.0271 9.82001 11.0464 10.0894 10.9114 10.2843L10.8536 10.3536L6.35355 14.8536C6.15829 15.0488 5.84171 15.0488 5.64645 14.8536C5.47288 14.68 5.4536 14.4106 5.58859 14.2157L5.64645 14.1464L9.79289 10L5.64645 5.85355C5.45118 5.65829 5.45118 5.34171 5.64645 5.14645Z",fill:"currentColor"})),lo=t("svg",{viewBox:"0 0 20 20",fill:"none",xmlns:"http://www.w3.org/2000/svg"},t("path",{d:"M4.089 4.216l.057-.07a.5.5 0 0 1 .638-.057l.07.057L10 9.293l5.146-5.147a.5.5 0 0 1 .638-.057l.07.057a.5.5 0 0 1 .057.638l-.057.07L10.707 10l5.147 5.146a.5.5 0 0 1 .057.638l-.057.07a.5.5 0 0 1-.638.057l-.07-.057L10 10.707l-5.146 5.147a.5.5 0 0 1-.638.057l-.07-.057a.5.5 0 0 1-.057-.638l.057-.07L9.293 10L4.146 4.854a.5.5 0 0 1-.057-.638l.057-.07l-.057.07z",fill:"currentColor"})),so=U([U("body >",[p("image-container","position: fixed;")]),p("image-preview-container",`
 position: fixed;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 display: flex;
 `),p("image-preview-overlay",`
 z-index: -1;
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 background: rgba(0, 0, 0, .3);
 `,[$e()]),p("image-preview-toolbar",`
 z-index: 1;
 position: absolute;
 left: 50%;
 transform: translateX(-50%);
 border-radius: var(--n-toolbar-border-radius);
 height: 48px;
 bottom: 40px;
 padding: 0 12px;
 background: var(--n-toolbar-color);
 box-shadow: var(--n-toolbar-box-shadow);
 color: var(--n-toolbar-icon-color);
 transition: color .3s var(--n-bezier);
 display: flex;
 align-items: center;
 `,[p("base-icon",`
 padding: 0 8px;
 font-size: 28px;
 cursor: pointer;
 `),$e()]),p("image-preview-wrapper",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 display: flex;
 pointer-events: none;
 `,[Lt()]),p("image-preview",`
 user-select: none;
 -webkit-user-select: none;
 pointer-events: all;
 margin: auto;
 max-height: calc(100vh - 32px);
 max-width: calc(100vw - 32px);
 transition: transform .3s var(--n-bezier);
 `),p("image",`
 display: inline-flex;
 max-height: 100%;
 max-width: 100%;
 `,[Tt("preview-disabled",`
 cursor: pointer;
 `),U("img",`
 border-radius: inherit;
 `)])]),he=32,gt=X({name:"ImagePreview",props:Object.assign(Object.assign({},Te),{onNext:Function,onPrev:Function,clsPrefix:{type:String,required:!0}}),setup(e){const o=le("Image","-image",so,io,e,N(e,"clsPrefix"));let r=null;const i=V(null),n=V(null),s=V(void 0),d=V(!1),f=V(!1),{localeRef:u}=Jt("Image");function a(){const{value:g}=n;if(!r||!g)return;const{style:w}=g,h=r.getBoundingClientRect(),B=h.left+h.width/2,I=h.top+h.height/2;w.transformOrigin=`${B}px ${I}px`}function l(g){var w,h;switch(g.key){case" ":g.preventDefault();break;case"ArrowLeft":(w=e.onPrev)===null||w===void 0||w.call(e);break;case"ArrowRight":(h=e.onNext)===null||h===void 0||h.call(e);break;case"Escape":Oe();break}}Ot(d,g=>{g?xe("keydown",document,l):fe("keydown",document,l)}),Xe(()=>{fe("keydown",document,l)});let c=0,C=0,v=0,R=0,x=0,L=0,j=0,z=0,S=!1;function D(g){const{clientX:w,clientY:h}=g;v=w-c,R=h-C,Mt(q)}function b(g){const{mouseUpClientX:w,mouseUpClientY:h,mouseDownClientX:B,mouseDownClientY:I}=g,Z=B-w,K=I-h,J=`vertical${K>0?"Top":"Bottom"}`,te=`horizontal${Z>0?"Left":"Right"}`;return{moveVerticalDirection:J,moveHorizontalDirection:te,deltaHorizontal:Z,deltaVertical:K}}function y(g){const{value:w}=i;if(!w)return{offsetX:0,offsetY:0};const h=w.getBoundingClientRect(),{moveVerticalDirection:B,moveHorizontalDirection:I,deltaHorizontal:Z,deltaVertical:K}=g||{};let J=0,te=0;return h.width<=window.innerWidth?J=0:h.left>0?J=(h.width-window.innerWidth)/2:h.right<window.innerWidth?J=-(h.width-window.innerWidth)/2:I==="horizontalRight"?J=Math.min((h.width-window.innerWidth)/2,x-(Z!=null?Z:0)):J=Math.max(-((h.width-window.innerWidth)/2),x-(Z!=null?Z:0)),h.height<=window.innerHeight?te=0:h.top>0?te=(h.height-window.innerHeight)/2:h.bottom<window.innerHeight?te=-(h.height-window.innerHeight)/2:B==="verticalBottom"?te=Math.min((h.height-window.innerHeight)/2,L-(K!=null?K:0)):te=Math.max(-((h.height-window.innerHeight)/2),L-(K!=null?K:0)),{offsetX:J,offsetY:te}}function k(g){fe("mousemove",document,D),fe("mouseup",document,k);const{clientX:w,clientY:h}=g;S=!1;const B=b({mouseUpClientX:w,mouseUpClientY:h,mouseDownClientX:j,mouseDownClientY:z}),I=y(B);v=I.offsetX,R=I.offsetY,q()}const E=re(ft,null);function m(g){var w,h;if((h=(w=E==null?void 0:E.previewedImgPropsRef.value)===null||w===void 0?void 0:w.onMousedown)===null||h===void 0||h.call(w,g),g.button!==0)return;const{clientX:B,clientY:I}=g;S=!0,c=B-v,C=I-R,x=v,L=R,j=B,z=I,q(),xe("mousemove",document,D),xe("mouseup",document,k)}function M(g){var w,h;(h=(w=E==null?void 0:E.previewedImgPropsRef.value)===null||w===void 0?void 0:w.onDblclick)===null||h===void 0||h.call(w,g);const B=ce();P=P===B?1:B,q()}const O=1.5;let W=0,P=1,F=0;function _(){P=1,W=0}function A(){var g;_(),F=0,(g=e.onPrev)===null||g===void 0||g.call(e)}function Y(){var g;_(),F=0,(g=e.onNext)===null||g===void 0||g.call(e)}function G(){F-=90,q()}function oe(){F+=90,q()}function me(){const{value:g}=i;if(!g)return 1;const{innerWidth:w,innerHeight:h}=window,B=Math.max(1,g.naturalHeight/(h-he)),I=Math.max(1,g.naturalWidth/(w-he));return Math.max(3,B*2,I*2)}function ce(){const{value:g}=i;if(!g)return 1;const{innerWidth:w,innerHeight:h}=window,B=g.naturalHeight/(h-he),I=g.naturalWidth/(w-he);return B<1&&I<1?1:Math.max(B,I)}function be(){const g=me();P<g&&(W+=1,P=Math.min(g,Math.pow(O,W)),q())}function we(){if(P>.5){const g=P;W-=1,P=Math.max(.5,Math.pow(O,W));const w=g-P;q(!1);const h=y();P+=w,q(!1),P-=w,v=h.offsetX,R=h.offsetY,q()}}function q(g=!0){var w;const{value:h}=i;if(!h)return;const{style:B}=h,I=Dt((w=E==null?void 0:E.previewedImgPropsRef.value)===null||w===void 0?void 0:w.style);let Z="";if(typeof I=="string")Z=I+";";else for(const J in I)Z+=`${Zr(J)}: ${I[J]};`;const K=`transform-origin: center; transform: translateX(${v}px) translateY(${R}px) rotate(${F}deg) scale(${P});`;S?B.cssText=Z+"cursor: grabbing; transition: none;"+K:B.cssText=Z+"cursor: grab;"+K+(g?"":"transition: none;"),g||h.offsetHeight}function Oe(){d.value=!d.value,f.value=!0}function yt(){P=ce(),W=Math.ceil(Math.log(P)/Math.log(O)),v=0,R=0,q()}const Ct={setPreviewSrc:g=>{s.value=g},setThumbnailEl:g=>{r=g},toggleShow:Oe};function Rt(g,w){if(e.showToolbarTooltip){const{value:h}=o;return t(er,{to:!1,theme:h.peers.Tooltip,themeOverrides:h.peerOverrides.Tooltip,keepAliveOnHover:!1},{default:()=>u.value[w],trigger:()=>g})}else return g}const Be=T(()=>{const{common:{cubicBezierEaseInOut:g},self:{toolbarIconColor:w,toolbarBorderRadius:h,toolbarBoxShadow:B,toolbarColor:I}}=o.value;return{"--n-bezier":g,"--n-toolbar-icon-color":w,"--n-toolbar-color":I,"--n-toolbar-border-radius":h,"--n-toolbar-box-shadow":B}}),{inlineThemeDisabled:Ie}=de(),ie=Ie?Pe("image-preview",void 0,Be,e):void 0;return Object.assign({previewRef:i,previewWrapperRef:n,previewSrc:s,show:d,appear:Bt(),displayed:f,previewedImgProps:E==null?void 0:E.previewedImgPropsRef,handleWheel(g){g.preventDefault()},handlePreviewMousedown:m,handlePreviewDblclick:M,syncTransformOrigin:a,handleAfterLeave:()=>{_(),F=0,f.value=!1},handleDragStart:g=>{var w,h;(h=(w=E==null?void 0:E.previewedImgPropsRef.value)===null||w===void 0?void 0:w.onDragstart)===null||h===void 0||h.call(w,g),g.preventDefault()},zoomIn:be,zoomOut:we,rotateCounterclockwise:G,rotateClockwise:oe,handleSwitchPrev:A,handleSwitchNext:Y,withTooltip:Rt,resizeToOrignalImageSize:yt,cssVars:Ie?void 0:Be,themeClass:ie==null?void 0:ie.themeClass,onRender:ie==null?void 0:ie.onRender},Ct)},render(){var e,o;const{clsPrefix:r}=this;return t(Ce,null,(o=(e=this.$slots).default)===null||o===void 0?void 0:o.call(e),t(It,{show:this.show},{default:()=>{var i;return this.show||this.displayed?((i=this.onRender)===null||i===void 0||i.call(this),ze(t("div",{class:[`${r}-image-preview-container`,this.themeClass],style:this.cssVars,onWheel:this.handleWheel},t(ye,{name:"fade-in-transition",appear:this.appear},{default:()=>this.show?t("div",{class:`${r}-image-preview-overlay`,onClick:this.toggleShow}):null}),this.showToolbar?t(ye,{name:"fade-in-transition",appear:this.appear},{default:()=>{if(!this.show)return null;const{withTooltip:n}=this;return t("div",{class:`${r}-image-preview-toolbar`},this.onPrev?t(Ce,null,n(t(H,{clsPrefix:r,onClick:this.handleSwitchPrev},{default:()=>no}),"tipPrevious"),n(t(H,{clsPrefix:r,onClick:this.handleSwitchNext},{default:()=>ao}),"tipNext")):null,n(t(H,{clsPrefix:r,onClick:this.rotateCounterclockwise},{default:()=>t(Qr,null)}),"tipCounterclockwise"),n(t(H,{clsPrefix:r,onClick:this.rotateClockwise},{default:()=>t(Jr,null)}),"tipClockwise"),n(t(H,{clsPrefix:r,onClick:this.resizeToOrignalImageSize},{default:()=>t(ro,null)}),"tipOriginalSize"),n(t(H,{clsPrefix:r,onClick:this.zoomOut},{default:()=>t(to,null)}),"tipZoomOut"),n(t(H,{clsPrefix:r,onClick:this.zoomIn},{default:()=>t(eo,null)}),"tipZoomIn"),n(t(H,{clsPrefix:r,onClick:this.toggleShow},{default:()=>lo}),"tipClose"))}}):null,t(ye,{name:"fade-in-scale-up-transition",onAfterLeave:this.handleAfterLeave,appear:this.appear,onEnter:this.syncTransformOrigin,onBeforeLeave:this.syncTransformOrigin},{default:()=>{const{previewedImgProps:n={}}=this;return ze(t("div",{class:`${r}-image-preview-wrapper`,ref:"previewWrapperRef"},t("img",Object.assign({},n,{draggable:!1,onMousedown:this.handlePreviewMousedown,onDblclick:this.handlePreviewDblclick,class:[`${r}-image-preview`,n.class],key:this.previewSrc,src:this.previewSrc,ref:"previewRef",onDragstart:this.handleDragStart}))),[[zt,this.show]])}})),[[$t,{enabled:this.show}]])):null}}))}}),ht=ke("n-image-group"),uo=Te,co=X({name:"ImageGroup",props:uo,setup(e){let o;const{mergedClsPrefixRef:r}=de(e),i=`c${Re()}`,n=_t(),s=u=>{var a;o=u,(a=f.value)===null||a===void 0||a.setPreviewSrc(u)};function d(u){if(!(n!=null&&n.proxy))return;const l=n.proxy.$el.parentElement.querySelectorAll(`[data-group-id=${i}]:not([data-error=true])`);if(!l.length)return;const c=Array.from(l).findIndex(C=>C.dataset.previewSrc===o);~c?s(l[(c+u+l.length)%l.length].dataset.previewSrc):s(l[0].dataset.previewSrc)}Le(ht,{mergedClsPrefixRef:r,setPreviewSrc:s,setThumbnailEl:u=>{var a;(a=f.value)===null||a===void 0||a.setThumbnailEl(u)},toggleShow:()=>{var u;(u=f.value)===null||u===void 0||u.toggleShow()},groupId:i});const f=V(null);return{mergedClsPrefix:r,previewInstRef:f,next:()=>{d(1)},prev:()=>{d(-1)}}},render(){return t(gt,{theme:this.theme,themeOverrides:this.themeOverrides,clsPrefix:this.mergedClsPrefix,ref:"previewInstRef",onPrev:this.prev,onNext:this.next,showToolbar:this.showToolbar,showToolbarTooltip:this.showToolbarTooltip},this.$slots)}}),fo=Object.assign({alt:String,height:[String,Number],imgProps:Object,previewedImgProps:Object,lazy:Boolean,intersectionObserverOptions:Object,objectFit:{type:String,default:"fill"},previewSrc:String,fallbackSrc:String,width:[String,Number],src:String,previewDisabled:Boolean,loadDescription:String,onError:Function,onLoad:Function},Te),go=X({name:"Image",props:fo,inheritAttrs:!1,setup(e){const o=V(null),r=V(!1),i=V(null),n=re(ht,null),{mergedClsPrefixRef:s}=n||de(e),d={click:()=>{if(e.previewDisabled||r.value)return;const a=e.previewSrc||e.src;if(n){n.setPreviewSrc(a),n.setThumbnailEl(o.value),n.toggleShow();return}const{value:l}=i;!l||(l.setPreviewSrc(a),l.setThumbnailEl(o.value),l.toggleShow())}},f=V(!e.lazy);De(()=>{var a;(a=o.value)===null||a===void 0||a.setAttribute("data-group-id",(n==null?void 0:n.groupId)||"")}),De(()=>{if(e.lazy&&e.intersectionObserverOptions){let a;const l=Se(()=>{a==null||a(),a=void 0,a=Gt(o.value,e.intersectionObserverOptions,f)});Xe(()=>{l(),a==null||a()})}}),Se(()=>{var a;e.src,(a=e.imgProps)===null||a===void 0||a.src,r.value=!1});const u=V(!1);return Le(ft,{previewedImgPropsRef:N(e,"previewedImgProps")}),Object.assign({mergedClsPrefix:s,groupId:n==null?void 0:n.groupId,previewInstRef:i,imageRef:o,showError:r,shouldStartLoading:f,loaded:u,mergedOnClick:a=>{var l,c;d.click(),(c=(l=e.imgProps)===null||l===void 0?void 0:l.onClick)===null||c===void 0||c.call(l,a)},mergedOnError:a=>{if(!f.value)return;r.value=!0;const{onError:l,imgProps:{onError:c}={}}=e;l==null||l(a),c==null||c(a)},mergedOnLoad:a=>{const{onLoad:l,imgProps:{onLoad:c}={}}=e;l==null||l(a),c==null||c(a),u.value=!0}},d)},render(){var e,o;const{mergedClsPrefix:r,imgProps:i={},loaded:n,$attrs:s,lazy:d}=this,f=(o=(e=this.$slots).placeholder)===null||o===void 0?void 0:o.call(e),u=this.src||i.src,a=t("img",Object.assign(Object.assign({},i),{ref:"imageRef",width:this.width||i.width,height:this.height||i.height,src:this.showError?this.fallbackSrc:d&&this.intersectionObserverOptions?this.shouldStartLoading?u:void 0:u,alt:this.alt||i.alt,"aria-label":this.alt||i.alt,onClick:this.mergedOnClick,onError:this.mergedOnError,onLoad:this.mergedOnLoad,loading:Kt&&d&&!this.intersectionObserverOptions?"lazy":"eager",style:[i.style||"",f&&!n?{height:"0",width:"0",visibility:"hidden"}:"",{objectFit:this.objectFit}],"data-error":this.showError,"data-preview-src":this.previewSrc||this.src}));return t("div",Object.assign({},s,{role:"none",class:[s.class,`${r}-image`,(this.previewDisabled||this.showError)&&`${r}-image--preview-disabled`]}),this.groupId?a:t(gt,{theme:this.theme,themeOverrides:this.themeOverrides,clsPrefix:r,ref:"previewInstRef",showToolbar:this.showToolbar,showToolbarTooltip:this.showToolbarTooltip},{default:()=>a}),!n&&f)}}),ho=U([p("progress",{display:"inline-block"},[p("progress-icon",`
 color: var(--n-icon-color);
 transition: color .3s var(--n-bezier);
 `),$("line",`
 width: 100%;
 display: block;
 `,[p("progress-content",`
 display: flex;
 align-items: center;
 `,[p("progress-graph",{flex:1})]),p("progress-custom-content",{marginLeft:"14px"}),p("progress-icon",`
 width: 30px;
 padding-left: 14px;
 height: var(--n-icon-size-line);
 line-height: var(--n-icon-size-line);
 font-size: var(--n-icon-size-line);
 `,[$("as-text",`
 color: var(--n-text-color-line-outer);
 text-align: center;
 width: 40px;
 font-size: var(--n-font-size);
 padding-left: 4px;
 transition: color .3s var(--n-bezier);
 `)])]),$("circle, dashboard",{width:"120px"},[p("progress-custom-content",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 `),p("progress-text",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: inherit;
 font-size: var(--n-font-size-circle);
 color: var(--n-text-color-circle);
 font-weight: var(--n-font-weight-circle);
 transition: color .3s var(--n-bezier);
 white-space: nowrap;
 `),p("progress-icon",`
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 color: var(--n-icon-color);
 font-size: var(--n-icon-size-circle);
 `)]),$("multiple-circle",`
 width: 200px;
 color: inherit;
 `,[p("progress-text",`
 font-weight: var(--n-font-weight-circle);
 color: var(--n-text-color-circle);
 position: absolute;
 left: 50%;
 top: 50%;
 transform: translateX(-50%) translateY(-50%);
 display: flex;
 align-items: center;
 justify-content: center;
 transition: color .3s var(--n-bezier);
 `)]),p("progress-content",{position:"relative"}),p("progress-graph",{position:"relative"},[p("progress-graph-circle",[U("svg",{verticalAlign:"bottom"}),p("progress-graph-circle-fill",`
 stroke: var(--n-fill-color);
 transition:
 opacity .3s var(--n-bezier),
 stroke .3s var(--n-bezier),
 stroke-dasharray .3s var(--n-bezier);
 `,[$("empty",{opacity:0})]),p("progress-graph-circle-rail",`
 transition: stroke .3s var(--n-bezier);
 overflow: hidden;
 stroke: var(--n-rail-color);
 `)]),p("progress-graph-line",[$("indicator-inside",[p("progress-graph-line-rail",`
 height: 16px;
 line-height: 16px;
 border-radius: 10px;
 `,[p("progress-graph-line-fill",`
 height: inherit;
 border-radius: 10px;
 `),p("progress-graph-line-indicator",`
 background: #0000;
 white-space: nowrap;
 text-align: right;
 margin-left: 14px;
 margin-right: 14px;
 height: inherit;
 font-size: 12px;
 color: var(--n-text-color-line-inner);
 transition: color .3s var(--n-bezier);
 `)])]),$("indicator-inside-label",`
 height: 16px;
 display: flex;
 align-items: center;
 `,[p("progress-graph-line-rail",`
 flex: 1;
 transition: background-color .3s var(--n-bezier);
 `),p("progress-graph-line-indicator",`
 background: var(--n-fill-color);
 font-size: 12px;
 transform: translateZ(0);
 display: flex;
 vertical-align: middle;
 height: 16px;
 line-height: 16px;
 padding: 0 10px;
 border-radius: 10px;
 position: absolute;
 white-space: nowrap;
 color: var(--n-text-color-line-inner);
 transition:
 right .2s var(--n-bezier),
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `)]),p("progress-graph-line-rail",`
 position: relative;
 overflow: hidden;
 height: var(--n-rail-height);
 border-radius: 5px;
 background-color: var(--n-rail-color);
 transition: background-color .3s var(--n-bezier);
 `,[p("progress-graph-line-fill",`
 background: var(--n-fill-color);
 position: relative;
 border-radius: 5px;
 height: inherit;
 width: 100%;
 max-width: 0%;
 transition:
 background-color .3s var(--n-bezier),
 max-width .2s var(--n-bezier);
 `,[$("processing",[U("&::after",`
 content: "";
 background-image: var(--n-line-bg-processing);
 animation: progress-processing-animation 2s var(--n-bezier) infinite;
 `)])])])])])]),U("@keyframes progress-processing-animation",`
 0% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 100%;
 opacity: 1;
 }
 66% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 0;
 opacity: 0;
 }
 100% {
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 right: 0;
 opacity: 0;
 }
 `)]),po={success:t(qe,null),error:t(Ye,null),warning:t(Ge,null),info:t(Ke,null)},vo=X({name:"ProgressLine",props:{clsPrefix:{type:String,required:!0},percentage:{type:Number,default:0},railColor:String,railStyle:[String,Object],fillColor:String,status:{type:String,required:!0},indicatorPlacement:{type:String,required:!0},indicatorTextColor:String,unit:{type:String,default:"%"},processing:{type:Boolean,required:!0},showIndicator:{type:Boolean,required:!0},height:[String,Number],railBorderRadius:[String,Number],fillBorderRadius:[String,Number]},setup(e,{slots:o}){const r=T(()=>ne(e.height)),i=T(()=>e.railBorderRadius!==void 0?ne(e.railBorderRadius):e.height!==void 0?ne(e.height,{c:.5}):""),n=T(()=>e.fillBorderRadius!==void 0?ne(e.fillBorderRadius):e.railBorderRadius!==void 0?ne(e.railBorderRadius):e.height!==void 0?ne(e.height,{c:.5}):"");return()=>{const{indicatorPlacement:s,railColor:d,railStyle:f,percentage:u,unit:a,indicatorTextColor:l,status:c,showIndicator:C,fillColor:v,processing:R,clsPrefix:x}=e;return t("div",{class:`${x}-progress-content`,role:"none"},t("div",{class:`${x}-progress-graph`,"aria-hidden":!0},t("div",{class:[`${x}-progress-graph-line`,{[`${x}-progress-graph-line--indicator-${s}`]:!0}]},t("div",{class:`${x}-progress-graph-line-rail`,style:[{backgroundColor:d,height:r.value,borderRadius:i.value},f]},t("div",{class:[`${x}-progress-graph-line-fill`,R&&`${x}-progress-graph-line-fill--processing`],style:{maxWidth:`${e.percentage}%`,backgroundColor:v,height:r.value,lineHeight:r.value,borderRadius:n.value}},s==="inside"?t("div",{class:`${x}-progress-graph-line-indicator`,style:{color:l}},u,a):null)))),C&&s==="outside"?t("div",null,o.default?t("div",{class:`${x}-progress-custom-content`,style:{color:l},role:"none"},o.default()):c==="default"?t("div",{role:"none",class:`${x}-progress-icon ${x}-progress-icon--as-text`,style:{color:l}},u,a):t("div",{class:`${x}-progress-icon`,"aria-hidden":!0},t(H,{clsPrefix:x},{default:()=>po[c]}))):null)}}}),mo={success:t(qe,null),error:t(Ye,null),warning:t(Ge,null),info:t(Ke,null)},bo=X({name:"ProgressCircle",props:{clsPrefix:{type:String,required:!0},status:{type:String,required:!0},strokeWidth:{type:Number,required:!0},fillColor:String,railColor:String,railStyle:[String,Object],percentage:{type:Number,default:0},offsetDegree:{type:Number,default:0},showIndicator:{type:Boolean,required:!0},indicatorTextColor:String,unit:String,viewBoxWidth:{type:Number,required:!0},gapDegree:{type:Number,required:!0},gapOffsetDegree:{type:Number,default:0}},setup(e,{slots:o}){function r(i,n,s){const{gapDegree:d,viewBoxWidth:f,strokeWidth:u}=e,a=50,l=0,c=a,C=0,v=2*a,R=50+u/2,x=`M ${R},${R} m ${l},${c}
      a ${a},${a} 0 1 1 ${C},${-v}
      a ${a},${a} 0 1 1 ${-C},${v}`,L=Math.PI*2*a,j={stroke:s,strokeDasharray:`${i/100*(L-d)}px ${f*8}px`,strokeDashoffset:`-${d/2}px`,transformOrigin:n?"center":void 0,transform:n?`rotate(${n}deg)`:void 0};return{pathString:x,pathStyle:j}}return()=>{const{fillColor:i,railColor:n,strokeWidth:s,offsetDegree:d,status:f,percentage:u,showIndicator:a,indicatorTextColor:l,unit:c,gapOffsetDegree:C,clsPrefix:v}=e,{pathString:R,pathStyle:x}=r(100,0,n),{pathString:L,pathStyle:j}=r(u,d,i),z=100+s;return t("div",{class:`${v}-progress-content`,role:"none"},t("div",{class:`${v}-progress-graph`,"aria-hidden":!0},t("div",{class:`${v}-progress-graph-circle`,style:{transform:C?`rotate(${C}deg)`:void 0}},t("svg",{viewBox:`0 0 ${z} ${z}`},t("g",null,t("path",{class:`${v}-progress-graph-circle-rail`,d:R,"stroke-width":s,"stroke-linecap":"round",fill:"none",style:x})),t("g",null,t("path",{class:[`${v}-progress-graph-circle-fill`,u===0&&`${v}-progress-graph-circle-fill--empty`],d:L,"stroke-width":s,"stroke-linecap":"round",fill:"none",style:j}))))),a?t("div",null,o.default?t("div",{class:`${v}-progress-custom-content`,role:"none"},o.default()):f!=="default"?t("div",{class:`${v}-progress-icon`,"aria-hidden":!0},t(H,{clsPrefix:v},{default:()=>mo[f]})):t("div",{class:`${v}-progress-text`,style:{color:l},role:"none"},t("span",{class:`${v}-progress-text__percentage`},u),t("span",{class:`${v}-progress-text__unit`},c))):null)}}});function Ne(e,o,r=100){return`m ${r/2} ${r/2-e} a ${e} ${e} 0 1 1 0 ${2*e} a ${e} ${e} 0 1 1 0 -${2*e}`}const wo=X({name:"ProgressMultipleCircle",props:{clsPrefix:{type:String,required:!0},viewBoxWidth:{type:Number,required:!0},percentage:{type:Array,default:[0]},strokeWidth:{type:Number,required:!0},circleGap:{type:Number,required:!0},showIndicator:{type:Boolean,required:!0},fillColor:{type:Array,default:()=>[]},railColor:{type:Array,default:()=>[]},railStyle:{type:Array,default:()=>[]}},setup(e,{slots:o}){const r=T(()=>e.percentage.map((n,s)=>`${Math.PI*n/100*(e.viewBoxWidth/2-e.strokeWidth/2*(1+2*s)-e.circleGap*s)*2}, ${e.viewBoxWidth*8}`));return()=>{const{viewBoxWidth:i,strokeWidth:n,circleGap:s,showIndicator:d,fillColor:f,railColor:u,railStyle:a,percentage:l,clsPrefix:c}=e;return t("div",{class:`${c}-progress-content`,role:"none"},t("div",{class:`${c}-progress-graph`,"aria-hidden":!0},t("div",{class:`${c}-progress-graph-circle`},t("svg",{viewBox:`0 0 ${i} ${i}`},l.map((C,v)=>t("g",{key:v},t("path",{class:`${c}-progress-graph-circle-rail`,d:Ne(i/2-n/2*(1+2*v)-s*v,n,i),"stroke-width":n,"stroke-linecap":"round",fill:"none",style:[{strokeDashoffset:0,stroke:u[v]},a[v]]}),t("path",{class:[`${c}-progress-graph-circle-fill`,C===0&&`${c}-progress-graph-circle-fill--empty`],d:Ne(i/2-n/2*(1+2*v)-s*v,n,i),"stroke-width":n,"stroke-linecap":"round",fill:"none",style:{strokeDasharray:r.value[v],strokeDashoffset:0,stroke:f[v]}})))))),d&&o.default?t("div",null,t("div",{class:`${c}-progress-text`},o.default())):null)}}}),xo=Object.assign(Object.assign({},le.props),{processing:Boolean,type:{type:String,default:"line"},gapDegree:Number,gapOffsetDegree:Number,status:{type:String,default:"default"},railColor:[String,Array],railStyle:[String,Array],color:[String,Array],viewBoxWidth:{type:Number,default:100},strokeWidth:{type:Number,default:7},percentage:[Number,Array],unit:{type:String,default:"%"},showIndicator:{type:Boolean,default:!0},indicatorPosition:{type:String,default:"outside"},indicatorPlacement:{type:String,default:"outside"},indicatorTextColor:String,circleGap:{type:Number,default:1},height:Number,borderRadius:[String,Number],fillBorderRadius:[String,Number],offsetDegree:Number}),yo=X({name:"Progress",props:xo,setup(e){const o=T(()=>e.indicatorPlacement||e.indicatorPosition),r=T(()=>{if(e.gapDegree||e.gapDegree===0)return e.gapDegree;if(e.type==="dashboard")return 75}),{mergedClsPrefixRef:i,inlineThemeDisabled:n}=de(e),s=le("Progress","-progress",ho,Ut,e,i),d=T(()=>{const{status:u}=e,{common:{cubicBezierEaseInOut:a},self:{fontSize:l,fontSizeCircle:c,railColor:C,railHeight:v,iconSizeCircle:R,iconSizeLine:x,textColorCircle:L,textColorLineInner:j,textColorLineOuter:z,lineBgProcessing:S,fontWeightCircle:D,[Me("iconColor",u)]:b,[Me("fillColor",u)]:y}}=s.value;return{"--n-bezier":a,"--n-fill-color":y,"--n-font-size":l,"--n-font-size-circle":c,"--n-font-weight-circle":D,"--n-icon-color":b,"--n-icon-size-circle":R,"--n-icon-size-line":x,"--n-line-bg-processing":S,"--n-rail-color":C,"--n-rail-height":v,"--n-text-color-circle":L,"--n-text-color-line-inner":j,"--n-text-color-line-outer":z}}),f=n?Pe("progress",T(()=>e.status[0]),d,e):void 0;return{mergedClsPrefix:i,mergedIndicatorPlacement:o,gapDeg:r,cssVars:n?void 0:d,themeClass:f==null?void 0:f.themeClass,onRender:f==null?void 0:f.onRender}},render(){const{type:e,cssVars:o,indicatorTextColor:r,showIndicator:i,status:n,railColor:s,railStyle:d,color:f,percentage:u,viewBoxWidth:a,strokeWidth:l,mergedIndicatorPlacement:c,unit:C,borderRadius:v,fillBorderRadius:R,height:x,processing:L,circleGap:j,mergedClsPrefix:z,gapDeg:S,gapOffsetDegree:D,themeClass:b,$slots:y,onRender:k}=this;return k==null||k(),t("div",{class:[b,`${z}-progress`,`${z}-progress--${e}`,`${z}-progress--${n}`],style:o,"aria-valuemax":100,"aria-valuemin":0,"aria-valuenow":u,role:e==="circle"||e==="line"||e==="dashboard"?"progressbar":"none"},e==="circle"||e==="dashboard"?t(bo,{clsPrefix:z,status:n,showIndicator:i,indicatorTextColor:r,railColor:s,fillColor:f,railStyle:d,offsetDegree:this.offsetDegree,percentage:u,viewBoxWidth:a,strokeWidth:l,gapDegree:S===void 0?e==="dashboard"?75:0:S,gapOffsetDegree:D,unit:C},y):e==="line"?t(vo,{clsPrefix:z,status:n,showIndicator:i,indicatorTextColor:r,railColor:s,fillColor:f,railStyle:d,percentage:u,processing:L,indicatorPlacement:c,unit:C,fillBorderRadius:R,railBorderRadius:v,height:x},y):e==="multiple-circle"?t(wo,{clsPrefix:z,strokeWidth:l,railColor:s,fillColor:f,railStyle:d,viewBoxWidth:a,percentage:u,showIndicator:i,circleGap:j},y):null)}}),se=ke("n-upload"),pt="__UPLOAD_DRAGGER__",Co=X({name:"UploadDragger",[pt]:!0,setup(e,{slots:o}){const r=re(se,null);return r||ve("upload-dragger","`n-upload-dragger` must be placed inside `n-upload`."),()=>{const{mergedClsPrefixRef:{value:i},mergedDisabledRef:{value:n},maxReachedRef:{value:s}}=r;return t("div",{class:[`${i}-upload-dragger`,(n||s)&&`${i}-upload-dragger--disabled`]},o)}}});var vt=globalThis&&globalThis.__awaiter||function(e,o,r,i){function n(s){return s instanceof r?s:new r(function(d){d(s)})}return new(r||(r=Promise))(function(s,d){function f(l){try{a(i.next(l))}catch(c){d(c)}}function u(l){try{a(i.throw(l))}catch(c){d(c)}}function a(l){l.done?s(l.value):n(l.value).then(f,u)}a((i=i.apply(e,o||[])).next())})};const mt=e=>e.includes("image/"),He=(e="")=>{const o=e.split("/"),i=o[o.length-1].split(/#|\?/)[0];return(/\.[^./\\]*$/.exec(i)||[""])[0]},We=/(webp|svg|png|gif|jpg|jpeg|jfif|bmp|dpg|ico)$/i,bt=e=>{if(e.type)return mt(e.type);const o=He(e.name||"");if(We.test(o))return!0;const r=e.thumbnailUrl||e.url||"",i=He(r);return!!(/^data:image\//.test(r)||We.test(i))};function Ro(e){return vt(this,void 0,void 0,function*(){return yield new Promise(o=>{if(!e.type||!mt(e.type)){o("");return}o(window.URL.createObjectURL(e))})})}const So=jt&&window.FileReader&&window.File;function ko(e){return e.isDirectory}function Po(e){return e.isFile}function Lo(e,o){return vt(this,void 0,void 0,function*(){const r=[];let i,n=0;function s(){n++}function d(){n--,n||i(r)}function f(u){u.forEach(a=>{if(!!a){if(s(),o&&ko(a)){const l=a.createReader();s(),l.readEntries(c=>{f(c),d()},()=>{d()})}else Po(a)&&(s(),a.file(l=>{r.push({file:l,entry:a,source:"dnd"}),d()},()=>{d()}));d()}})}return yield new Promise(u=>{i=u,f(e)}),r})}function ue(e){const{id:o,name:r,percentage:i,status:n,url:s,file:d,thumbnailUrl:f,type:u,fullPath:a,batchId:l}=e;return{id:o,name:r,percentage:i!=null?i:null,status:n,url:s!=null?s:null,file:d!=null?d:null,thumbnailUrl:f!=null?f:null,type:u!=null?u:null,fullPath:a!=null?a:null,batchId:l!=null?l:null}}function To(e,o,r){return e=e.toLowerCase(),o=o.toLocaleLowerCase(),r=r.toLocaleLowerCase(),r.split(",").map(n=>n.trim()).filter(Boolean).some(n=>{if(n.startsWith(".")){if(e.endsWith(n))return!0}else if(n.includes("/")){const[s,d]=o.split("/"),[f,u]=n.split("/");if((f==="*"||s&&f&&f===s)&&(u==="*"||d&&u&&u===d))return!0}else return!0;return!1})}const Oo=(e,o)=>{if(!e)return;const r=document.createElement("a");r.href=e,o!==void 0&&(r.download=o),document.body.appendChild(r),r.click(),document.body.removeChild(r)},wt=X({name:"UploadTrigger",props:{abstract:Boolean},setup(e,{slots:o}){const r=re(se,null);r||ve("upload-trigger","`n-upload-trigger` must be placed inside `n-upload`.");const{mergedClsPrefixRef:i,mergedDisabledRef:n,maxReachedRef:s,listTypeRef:d,dragOverRef:f,openOpenFileDialog:u,draggerInsideRef:a,handleFileAddition:l,mergedDirectoryDndRef:c,triggerStyleRef:C}=r,v=T(()=>d.value==="image-card");function R(){n.value||s.value||u()}function x(S){S.preventDefault(),f.value=!0}function L(S){S.preventDefault(),f.value=!0}function j(S){S.preventDefault(),f.value=!1}function z(S){var D;if(S.preventDefault(),!a.value||n.value||s.value){f.value=!1;return}const b=(D=S.dataTransfer)===null||D===void 0?void 0:D.items;b!=null&&b.length?Lo(Array.from(b).map(y=>y.webkitGetAsEntry()),c.value).then(y=>{l(y)}).finally(()=>{f.value=!1}):f.value=!1}return()=>{var S;const{value:D}=i;return e.abstract?(S=o.default)===null||S===void 0?void 0:S.call(o,{handleClick:R,handleDrop:z,handleDragOver:x,handleDragEnter:L,handleDragLeave:j}):t("div",{class:[`${D}-upload-trigger`,(n.value||s.value)&&`${D}-upload-trigger--disabled`,v.value&&`${D}-upload-trigger--image-card`],style:C.value,onClick:R,onDrop:z,onDragover:x,onDragenter:L,onDragleave:j},v.value?t(Co,null,{default:()=>Et(o.default,()=>[t(H,{clsPrefix:D},{default:()=>t(Yt,null)})])}):o)}}}),Bo=X({name:"UploadProgress",props:{show:Boolean,percentage:{type:Number,required:!0},status:{type:String,required:!0}},setup(){return{mergedTheme:re(se).mergedThemeRef}},render(){return t(Je,null,{default:()=>this.show?t(yo,{type:"line",showIndicator:!1,percentage:this.percentage,status:this.status,height:2,theme:this.mergedTheme.peers.Progress,themeOverrides:this.mergedTheme.peerOverrides.Progress}):null})}}),Io=t("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 28 28"},t("g",{fill:"none"},t("path",{d:"M21.75 3A3.25 3.25 0 0 1 25 6.25v15.5A3.25 3.25 0 0 1 21.75 25H6.25A3.25 3.25 0 0 1 3 21.75V6.25A3.25 3.25 0 0 1 6.25 3h15.5zm.583 20.4l-7.807-7.68a.75.75 0 0 0-.968-.07l-.084.07l-7.808 7.68c.183.065.38.1.584.1h15.5c.204 0 .4-.035.583-.1l-7.807-7.68l7.807 7.68zM21.75 4.5H6.25A1.75 1.75 0 0 0 4.5 6.25v15.5c0 .208.036.408.103.593l7.82-7.692a2.25 2.25 0 0 1 3.026-.117l.129.117l7.82 7.692c.066-.185.102-.385.102-.593V6.25a1.75 1.75 0 0 0-1.75-1.75zm-3.25 3a2.5 2.5 0 1 1 0 5a2.5 2.5 0 0 1 0-5zm0 1.5a1 1 0 1 0 0 2a1 1 0 0 0 0-2z",fill:"currentColor"}))),$o=t("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 28 28"},t("g",{fill:"none"},t("path",{d:"M6.4 2A2.4 2.4 0 0 0 4 4.4v19.2A2.4 2.4 0 0 0 6.4 26h15.2a2.4 2.4 0 0 0 2.4-2.4V11.578c0-.729-.29-1.428-.805-1.944l-6.931-6.931A2.4 2.4 0 0 0 14.567 2H6.4zm-.9 2.4a.9.9 0 0 1 .9-.9H14V10a2 2 0 0 0 2 2h6.5v11.6a.9.9 0 0 1-.9.9H6.4a.9.9 0 0 1-.9-.9V4.4zm16.44 6.1H16a.5.5 0 0 1-.5-.5V4.06l6.44 6.44z",fill:"currentColor"})));var zo=globalThis&&globalThis.__awaiter||function(e,o,r,i){function n(s){return s instanceof r?s:new r(function(d){d(s)})}return new(r||(r=Promise))(function(s,d){function f(l){try{a(i.next(l))}catch(c){d(c)}}function u(l){try{a(i.throw(l))}catch(c){d(c)}}function a(l){l.done?s(l.value):n(l.value).then(f,u)}a((i=i.apply(e,o||[])).next())})};const pe={paddingMedium:"0 3px",heightMedium:"24px",iconSizeMedium:"18px"},Do=X({name:"UploadFile",props:{clsPrefix:{type:String,required:!0},file:{type:Object,required:!0},listType:{type:String,required:!0}},setup(e){const o=re(se),r=V(null),i=V(""),n=T(()=>{const{file:b}=e;return b.status==="finished"?"success":b.status==="error"?"error":"info"}),s=T(()=>{const{file:b}=e;if(b.status==="error")return"error"}),d=T(()=>{const{file:b}=e;return b.status==="uploading"}),f=T(()=>{if(!o.showCancelButtonRef.value)return!1;const{file:b}=e;return["uploading","pending","error"].includes(b.status)}),u=T(()=>{if(!o.showRemoveButtonRef.value)return!1;const{file:b}=e;return["finished"].includes(b.status)}),a=T(()=>{if(!o.showDownloadButtonRef.value)return!1;const{file:b}=e;return["finished"].includes(b.status)}),l=T(()=>{if(!o.showRetryButtonRef.value)return!1;const{file:b}=e;return["error"].includes(b.status)}),c=Ft(()=>i.value||e.file.thumbnailUrl||e.file.url),C=T(()=>{if(!o.showPreviewButtonRef.value)return!1;const{file:{status:b},listType:y}=e;return["finished"].includes(b)&&c.value&&y==="image-card"});function v(){o.submit(e.file.id)}function R(b){b.preventDefault();const{file:y}=e;["finished","pending","error"].includes(y.status)?L(y):["uploading"].includes(y.status)?z(y):Nt("upload","The button clicked type is unknown.")}function x(b){b.preventDefault(),j(e.file)}function L(b){const{xhrMap:y,doChange:k,onRemoveRef:{value:E},mergedFileListRef:{value:m}}=o;Promise.resolve(E?E({file:Object.assign({},b),fileList:m}):!0).then(M=>{if(M===!1)return;const O=Object.assign({},b,{status:"removed"});y.delete(b.id),k(O,void 0,{remove:!0})})}function j(b){const{onDownloadRef:{value:y}}=o;Promise.resolve(y?y(Object.assign({},b)):!0).then(k=>{k!==!1&&Oo(b.url,b.name)})}function z(b){const{xhrMap:y}=o,k=y.get(b.id);k==null||k.abort(),L(Object.assign({},b))}function S(){const{onPreviewRef:{value:b}}=o;if(b)b(e.file);else if(e.listType==="image-card"){const{value:y}=r;if(!y)return;y.click()}}const D=()=>zo(this,void 0,void 0,function*(){const{listType:b}=e;b!=="image"&&b!=="image-card"||o.shouldUseThumbnailUrlRef.value(e.file)&&(i.value=yield o.getFileThumbnailUrlResolver(e.file))});return Se(()=>{D()}),{mergedTheme:o.mergedThemeRef,progressStatus:n,buttonType:s,showProgress:d,disabled:o.mergedDisabledRef,showCancelButton:f,showRemoveButton:u,showDownloadButton:a,showRetryButton:l,showPreviewButton:C,mergedThumbnailUrl:c,shouldUseThumbnailUrl:o.shouldUseThumbnailUrlRef,renderIcon:o.renderIconRef,imageRef:r,handleRemoveOrCancelClick:R,handleDownloadClick:x,handleRetryClick:v,handlePreviewClick:S}},render(){const{clsPrefix:e,mergedTheme:o,listType:r,file:i,renderIcon:n}=this;let s;const d=r==="image";d||r==="image-card"?s=!this.shouldUseThumbnailUrl(i)||!this.mergedThumbnailUrl?t("span",{class:`${e}-upload-file-info__thumbnail`},n?n(i):bt(i)?t(H,{clsPrefix:e},{default:()=>Io}):t(H,{clsPrefix:e},{default:()=>$o})):t("a",{rel:"noopener noreferer",target:"_blank",href:i.url||void 0,class:`${e}-upload-file-info__thumbnail`,onClick:this.handlePreviewClick},r==="image-card"?t(go,{src:this.mergedThumbnailUrl||void 0,previewSrc:i.url||void 0,alt:i.name,ref:"imageRef"}):t("img",{src:this.mergedThumbnailUrl||void 0,alt:i.name})):s=t("span",{class:`${e}-upload-file-info__thumbnail`},n?n(i):t(H,{clsPrefix:e},{default:()=>t(Xr,null)}));const u=t(Bo,{show:this.showProgress,percentage:i.percentage||0,status:this.progressStatus}),a=r==="text"||r==="image";return t("div",{class:[`${e}-upload-file`,`${e}-upload-file--${this.progressStatus}-status`,i.url&&i.status!=="error"&&r!=="image-card"&&`${e}-upload-file--with-url`,`${e}-upload-file--${r}-type`]},t("div",{class:`${e}-upload-file-info`},s,t("div",{class:`${e}-upload-file-info__name`},a&&(i.url&&i.status!=="error"?t("a",{rel:"noopener noreferer",target:"_blank",href:i.url||void 0,onClick:this.handlePreviewClick},i.name):t("span",{onClick:this.handlePreviewClick},i.name)),d&&u),t("div",{class:[`${e}-upload-file-info__action`,`${e}-upload-file-info__action--${r}-type`]},this.showPreviewButton?t(ge,{key:"preview",quaternary:!0,type:this.buttonType,onClick:this.handlePreviewClick,theme:o.peers.Button,themeOverrides:o.peerOverrides.Button,builtinThemeOverrides:pe},{icon:()=>t(H,{clsPrefix:e},{default:()=>t(Qt,null)})}):null,(this.showRemoveButton||this.showCancelButton)&&!this.disabled&&t(ge,{key:"cancelOrTrash",theme:o.peers.Button,themeOverrides:o.peerOverrides.Button,quaternary:!0,builtinThemeOverrides:pe,type:this.buttonType,onClick:this.handleRemoveOrCancelClick},{icon:()=>t(At,null,{default:()=>this.showRemoveButton?t(H,{clsPrefix:e,key:"trash"},{default:()=>t(qr,null)}):t(H,{clsPrefix:e,key:"cancel"},{default:()=>t(Gr,null)})})}),this.showRetryButton&&!this.disabled&&t(ge,{key:"retry",quaternary:!0,type:this.buttonType,onClick:this.handleRetryClick,theme:o.peers.Button,themeOverrides:o.peerOverrides.Button,builtinThemeOverrides:pe},{icon:()=>t(H,{clsPrefix:e},{default:()=>t(Kr,null)})}),this.showDownloadButton?t(ge,{key:"download",quaternary:!0,type:this.buttonType,onClick:this.handleDownloadClick,theme:o.peers.Button,themeOverrides:o.peerOverrides.Button,builtinThemeOverrides:pe},{icon:()=>t(H,{clsPrefix:e},{default:()=>t(Yr,null)})}):null)),!d&&u)}}),Mo=X({name:"UploadFileList",setup(e,{slots:o}){const r=re(se,null);r||ve("upload-file-list","`n-upload-file-list` must be placed inside `n-upload`.");const{abstractRef:i,mergedClsPrefixRef:n,listTypeRef:s,mergedFileListRef:d,fileListStyleRef:f,cssVarsRef:u,themeClassRef:a,maxReachedRef:l,showTriggerRef:c,imageGroupPropsRef:C}=r,v=T(()=>s.value==="image-card"),R=()=>d.value.map(L=>t(Do,{clsPrefix:n.value,key:L.id,file:L,listType:s.value})),x=()=>v.value?t(co,Object.assign({},C.value),{default:R}):t(Je,{group:!0},{default:R});return()=>{const{value:L}=n,{value:j}=i;return t("div",{class:[`${L}-upload-file-list`,v.value&&`${L}-upload-file-list--grid`,j?a==null?void 0:a.value:void 0],style:[j&&u?u.value:"",f.value]},x(),c.value&&!l.value&&v.value&&t(wt,null,o))}}}),_o=U([p("upload","width: 100%;",[$("dragger-inside",[p("upload-trigger",`
 display: block;
 `)]),$("drag-over",[p("upload-dragger",`
 border: var(--n-dragger-border-hover);
 `)])]),p("upload-dragger",`
 cursor: pointer;
 box-sizing: border-box;
 width: 100%;
 text-align: center;
 border-radius: var(--n-border-radius);
 padding: 24px;
 opacity: 1;
 transition:
 opacity .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 background-color: var(--n-dragger-color);
 border: var(--n-dragger-border);
 `,[U("&:hover",`
 border: var(--n-dragger-border-hover);
 `),$("disabled",`
 cursor: not-allowed;
 `)]),p("upload-trigger",`
 display: inline-block;
 box-sizing: border-box;
 opacity: 1;
 transition: opacity .3s var(--n-bezier);
 `,[U("+",[p("upload-file-list","margin-top: 8px;")]),$("disabled",`
 opacity: var(--n-item-disabled-opacity);
 cursor: not-allowed;
 `),$("image-card",`
 width: 96px;
 height: 96px;
 `,[p("base-icon",`
 font-size: 24px;
 `),p("upload-dragger",`
 padding: 0;
 height: 100%;
 width: 100%;
 display: flex;
 align-items: center;
 justify-content: center;
 `)])]),p("upload-file-list",`
 line-height: var(--n-line-height);
 opacity: 1;
 transition: opacity .3s var(--n-bezier);
 `,[U("a, img","outline: none;"),$("disabled",`
 opacity: var(--n-item-disabled-opacity);
 cursor: not-allowed;
 `,[p("upload-file","cursor: not-allowed;")]),$("grid",`
 display: grid;
 grid-template-columns: repeat(auto-fill, 96px);
 grid-gap: 8px;
 margin-top: 0;
 `),p("upload-file",`
 display: block;
 box-sizing: border-box;
 cursor: default;
 padding: 0px 12px 0 6px;
 transition: background-color .3s var(--n-bezier);
 border-radius: var(--n-border-radius);
 `,[_e(),p("progress",[_e({foldPadding:!0})]),U("&:hover",`
 background-color: var(--n-item-color-hover);
 `,[p("upload-file-info",[Q("action",`
 opacity: 1;
 `)])]),$("image-type",`
 border-radius: var(--n-border-radius);
 text-decoration: underline;
 text-decoration-color: #0000;
 `,[p("upload-file-info",`
 padding-top: 0px;
 padding-bottom: 0px;
 width: 100%;
 height: 100%;
 display: flex;
 justify-content: space-between;
 align-items: center;
 padding: 6px 0;
 `,[p("progress",`
 padding: 2px 0;
 margin-bottom: 0;
 `),Q("name",`
 padding: 0 8px;
 `),Q("thumbnail",`
 width: 32px;
 height: 32px;
 font-size: 28px;
 display: flex;
 justify-content: center;
 align-items: center;
 `,[U("img",`
 width: 100%;
 `)])])]),$("text-type",[p("progress",`
 box-sizing: border-box;
 padding-bottom: 6px;
 margin-bottom: 6px;
 `)]),$("image-card-type",`
 position: relative;
 width: 96px;
 height: 96px;
 border: var(--n-item-border-image-card);
 border-radius: var(--n-border-radius);
 padding: 0;
 display: flex;
 align-items: center;
 justify-content: center;
 transition: border-color .3s var(--n-bezier), background-color .3s var(--n-bezier);
 border-radius: var(--n-border-radius);
 overflow: hidden;
 `,[p("progress",`
 position: absolute;
 left: 8px;
 bottom: 8px;
 right: 8px;
 width: unset;
 `),p("upload-file-info",`
 padding: 0;
 width: 100%;
 height: 100%;
 `,[Q("thumbnail",`
 width: 100%;
 height: 100%;
 display: flex;
 flex-direction: column;
 align-items: center;
 justify-content: center;
 font-size: 36px;
 `,[U("img",`
 width: 100%;
 `)])]),U("&::before",`
 position: absolute;
 z-index: 1;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 border-radius: inherit;
 opacity: 0;
 transition: opacity .2s var(--n-bezier);
 content: "";
 `),U("&:hover",[U("&::before","opacity: 1;"),p("upload-file-info",[Q("thumbnail","opacity: .12;")])])]),$("error-status",[U("&:hover",`
 background-color: var(--n-item-color-hover-error);
 `),p("upload-file-info",[Q("name","color: var(--n-item-text-color-error);"),Q("thumbnail","color: var(--n-item-text-color-error);")]),$("image-card-type",`
 border: var(--n-item-border-image-card-error);
 `)]),$("with-url",`
 cursor: pointer;
 `,[p("upload-file-info",[Q("name",`
 color: var(--n-item-text-color-success);
 text-decoration-color: var(--n-item-text-color-success);
 `,[U("a",`
 text-decoration: underline;
 `)])])]),p("upload-file-info",`
 position: relative;
 padding-top: 6px;
 padding-bottom: 6px;
 display: flex;
 flex-wrap: nowrap;
 `,[Q("thumbnail",`
 font-size: 18px;
 opacity: 1;
 transition: opacity .2s var(--n-bezier);
 color: var(--n-item-icon-color);
 `,[p("base-icon",`
 margin-right: 2px;
 vertical-align: middle;
 transition: color .3s var(--n-bezier);
 `)]),Q("action",`
 padding-top: inherit;
 padding-bottom: inherit;
 position: absolute;
 right: 0;
 top: 0;
 bottom: 0;
 width: 80px;
 display: flex;
 align-items: center;
 transition: opacity .2s var(--n-bezier);
 justify-content: flex-end;
 opacity: 0;
 `,[p("button",[U("&:not(:last-child)",{marginRight:"4px"}),p("base-icon",[U("svg",[Ht()])])]),$("image-type",`
 position: relative;
 max-width: 80px;
 width: auto;
 `),$("image-card-type",`
 z-index: 2;
 position: absolute;
 width: 100%;
 height: 100%;
 left: 0;
 right: 0;
 bottom: 0;
 top: 0;
 display: flex;
 justify-content: center;
 align-items: center;
 `)]),Q("name",`
 color: var(--n-item-text-color);
 flex: 1;
 display: flex;
 justify-content: center;
 text-overflow: ellipsis;
 overflow: hidden;
 flex-direction: column;
 text-decoration-color: #0000;
 font-size: var(--n-font-size);
 transition:
 color .3s var(--n-bezier),
 text-decoration-color .3s var(--n-bezier); 
 `,[U("a",`
 color: inherit;
 text-decoration: underline;
 `)])])])]),p("upload-file-input",`
 display: block;
 width: 0;
 height: 0;
 opacity: 0;
 `)]);var Ve=globalThis&&globalThis.__awaiter||function(e,o,r,i){function n(s){return s instanceof r?s:new r(function(d){d(s)})}return new(r||(r=Promise))(function(s,d){function f(l){try{a(i.next(l))}catch(c){d(c)}}function u(l){try{a(i.throw(l))}catch(c){d(c)}}function a(l){l.done?s(l.value):n(l.value).then(f,u)}a((i=i.apply(e,o||[])).next())})};function Uo(e,o,r){const{doChange:i,xhrMap:n}=e;let s=0;function d(u){var a;let l=Object.assign({},o,{status:"error",percentage:s});n.delete(o.id),l=ue(((a=e.onError)===null||a===void 0?void 0:a.call(e,{file:l,event:u}))||l),i(l,u)}function f(u){var a;if(e.isErrorState){if(e.isErrorState(r)){d(u);return}}else if(r.status<200||r.status>=300){d(u);return}let l=Object.assign({},o,{status:"finished",percentage:s});n.delete(o.id),l=ue(((a=e.onFinish)===null||a===void 0?void 0:a.call(e,{file:l,event:u}))||l),i(l,u)}return{handleXHRLoad:f,handleXHRError:d,handleXHRAbort(u){const a=Object.assign({},o,{status:"removed",file:null,percentage:s});n.delete(o.id),i(a,u)},handleXHRProgress(u){const a=Object.assign({},o,{status:"uploading"});if(u.lengthComputable){const l=Math.ceil(u.loaded/u.total*100);a.percentage=l,s=l}i(a,u)}}}function jo(e){const{inst:o,file:r,data:i,headers:n,withCredentials:s,action:d,customRequest:f}=e,{doChange:u}=e.inst;let a=0;f({file:r,data:i,headers:n,withCredentials:s,action:d,onProgress(l){const c=Object.assign({},r,{status:"uploading"}),C=l.percent;c.percentage=C,a=C,u(c)},onFinish(){var l;let c=Object.assign({},r,{status:"finished",percentage:a});c=ue(((l=o.onFinish)===null||l===void 0?void 0:l.call(o,{file:c}))||c),u(c)},onError(){var l;let c=Object.assign({},r,{status:"error",percentage:a});c=ue(((l=o.onError)===null||l===void 0?void 0:l.call(o,{file:c}))||c),u(c)}})}function Eo(e,o,r){const i=Uo(e,o,r);r.onabort=i.handleXHRAbort,r.onerror=i.handleXHRError,r.onload=i.handleXHRLoad,r.upload&&(r.upload.onprogress=i.handleXHRProgress)}function xt(e,o){return typeof e=="function"?e({file:o}):e||{}}function Fo(e,o,r){const i=xt(o,r);!i||Object.keys(i).forEach(n=>{e.setRequestHeader(n,i[n])})}function Ao(e,o,r){const i=xt(o,r);!i||Object.keys(i).forEach(n=>{e.append(n,i[n])})}function No(e,o,r,{method:i,action:n,withCredentials:s,responseType:d,headers:f,data:u}){const a=new XMLHttpRequest;a.responseType=d,e.xhrMap.set(r.id,a),a.withCredentials=s;const l=new FormData;if(Ao(l,u,r),l.append(o,r.file),Eo(e,r,a),n!==void 0){a.open(i.toUpperCase(),n),Fo(a,f,r),a.send(l);const c=Object.assign({},r,{status:"uploading"});e.doChange(c)}}const Ho=Object.assign(Object.assign({},le.props),{name:{type:String,default:"file"},accept:String,action:String,customRequest:Function,directory:Boolean,directoryDnd:{type:Boolean,default:void 0},method:{type:String,default:"POST"},multiple:Boolean,showFileList:{type:Boolean,default:!0},data:[Object,Function],headers:[Object,Function],withCredentials:Boolean,responseType:{type:String,default:""},disabled:{type:Boolean,default:void 0},onChange:Function,onRemove:Function,onFinish:Function,onError:Function,onBeforeUpload:Function,isErrorState:Function,onDownload:Function,defaultUpload:{type:Boolean,default:!0},fileList:Array,"onUpdate:fileList":[Function,Array],onUpdateFileList:[Function,Array],fileListStyle:[String,Object],defaultFileList:{type:Array,default:()=>[]},showCancelButton:{type:Boolean,default:!0},showRemoveButton:{type:Boolean,default:!0},showDownloadButton:Boolean,showRetryButton:{type:Boolean,default:!0},showPreviewButton:{type:Boolean,default:!0},listType:{type:String,default:"text"},onPreview:Function,shouldUseThumbnailUrl:{type:Function,default:e=>So?bt(e):!1},createThumbnailUrl:Function,abstract:Boolean,max:Number,showTrigger:{type:Boolean,default:!0},imageGroupProps:Object,inputProps:Object,triggerStyle:[String,Object],renderIcon:Object}),Yo=X({name:"Upload",props:Ho,setup(e){e.abstract&&e.listType==="image-card"&&ve("upload","when the list-type is image-card, abstract is not supported.");const{mergedClsPrefixRef:o,inlineThemeDisabled:r}=de(e),i=le("Upload","-upload",_o,Wt,e,o),n=Vt(e),s=T(()=>{const{max:m}=e;return m!==void 0?v.value.length>=m:!1}),d=V(e.defaultFileList),f=N(e,"fileList"),u=V(null),a={value:!1},l=V(!1),c=new Map,C=Zt(f,d),v=T(()=>C.value.map(ue));function R(){var m;(m=u.value)===null||m===void 0||m.click()}function x(m){const M=m.target;z(M.files?Array.from(M.files).map(O=>({file:O,entry:null,source:"input"})):null,m),M.value=""}function L(m){const{"onUpdate:fileList":M,onUpdateFileList:O}=e;M&&Ue(M,m),O&&Ue(O,m),d.value=m}const j=T(()=>e.multiple||e.directory);function z(m,M){if(!m||m.length===0)return;const{onBeforeUpload:O}=e;m=j.value?m:[m[0]];const{max:W,accept:P}=e;m=m.filter(({file:_,source:A})=>A==="dnd"&&(P==null?void 0:P.trim())?To(_.name,_.type,P):!0),W&&(m=m.slice(0,W-v.value.length));const F=Re();Promise.all(m.map(({file:_,entry:A})=>Ve(this,void 0,void 0,function*(){var Y;const G={id:Re(),batchId:F,name:_.name,status:"pending",percentage:0,file:_,url:null,type:_.type,thumbnailUrl:null,fullPath:(Y=A==null?void 0:A.fullPath)!==null&&Y!==void 0?Y:`/${_.webkitRelativePath||_.name}`};return!O||(yield O({file:G,fileList:v.value}))!==!1?G:null}))).then(_=>Ve(this,void 0,void 0,function*(){let A=Promise.resolve();_.forEach(Y=>{A=A.then(qt).then(()=>{Y&&D(Y,M,{append:!0})})}),yield A})).then(()=>{e.defaultUpload&&S()})}function S(m){const{method:M,action:O,withCredentials:W,headers:P,data:F,name:_}=e,A=m!==void 0?v.value.filter(G=>G.id===m):v.value,Y=m!==void 0;A.forEach(G=>{const{status:oe}=G;(oe==="pending"||oe==="error"&&Y)&&(e.customRequest?jo({inst:{doChange:D,xhrMap:c,onFinish:e.onFinish,onError:e.onError},file:G,action:O,withCredentials:W,headers:P,data:F,customRequest:e.customRequest}):No({doChange:D,xhrMap:c,onFinish:e.onFinish,onError:e.onError,isErrorState:e.isErrorState},_,G,{method:M,action:O,withCredentials:W,responseType:e.responseType,headers:P,data:F}))})}const D=(m,M,O={append:!1,remove:!1})=>{const{append:W,remove:P}=O,F=Array.from(v.value),_=F.findIndex(A=>A.id===m.id);if(W||P||~_){W?F.push(m):P?F.splice(_,1):F.splice(_,1,m);const{onChange:A}=e;A&&A({file:m,fileList:F,event:M}),L(F)}};function b(m){var M;if(m.thumbnailUrl)return m.thumbnailUrl;const{createThumbnailUrl:O}=e;return O?(M=O(m.file,m))!==null&&M!==void 0?M:m.url||"":m.url?m.url:m.file?Ro(m.file):""}const y=T(()=>{const{common:{cubicBezierEaseInOut:m},self:{draggerColor:M,draggerBorder:O,draggerBorderHover:W,itemColorHover:P,itemColorHoverError:F,itemTextColorError:_,itemTextColorSuccess:A,itemTextColor:Y,itemIconColor:G,itemDisabledOpacity:oe,lineHeight:me,borderRadius:ce,fontSize:be,itemBorderImageCardError:we,itemBorderImageCard:q}}=i.value;return{"--n-bezier":m,"--n-border-radius":ce,"--n-dragger-border":O,"--n-dragger-border-hover":W,"--n-dragger-color":M,"--n-font-size":be,"--n-item-color-hover":P,"--n-item-color-hover-error":F,"--n-item-disabled-opacity":oe,"--n-item-icon-color":G,"--n-item-text-color":Y,"--n-item-text-color-error":_,"--n-item-text-color-success":A,"--n-line-height":me,"--n-item-border-image-card-error":we,"--n-item-border-image-card":q}}),k=r?Pe("upload",void 0,y,e):void 0;Le(se,{mergedClsPrefixRef:o,mergedThemeRef:i,showCancelButtonRef:N(e,"showCancelButton"),showDownloadButtonRef:N(e,"showDownloadButton"),showRemoveButtonRef:N(e,"showRemoveButton"),showRetryButtonRef:N(e,"showRetryButton"),onRemoveRef:N(e,"onRemove"),onDownloadRef:N(e,"onDownload"),mergedFileListRef:v,triggerStyleRef:N(e,"triggerStyle"),shouldUseThumbnailUrlRef:N(e,"shouldUseThumbnailUrl"),renderIconRef:N(e,"renderIcon"),xhrMap:c,submit:S,doChange:D,showPreviewButtonRef:N(e,"showPreviewButton"),onPreviewRef:N(e,"onPreview"),getFileThumbnailUrlResolver:b,listTypeRef:N(e,"listType"),dragOverRef:l,openOpenFileDialog:R,draggerInsideRef:a,handleFileAddition:z,mergedDisabledRef:n.mergedDisabledRef,maxReachedRef:s,fileListStyleRef:N(e,"fileListStyle"),abstractRef:N(e,"abstract"),acceptRef:N(e,"accept"),cssVarsRef:r?void 0:y,themeClassRef:k==null?void 0:k.themeClass,onRender:k==null?void 0:k.onRender,showTriggerRef:N(e,"showTrigger"),imageGroupPropsRef:N(e,"imageGroupProps"),mergedDirectoryDndRef:T(()=>{var m;return(m=e.directoryDnd)!==null&&m!==void 0?m:e.directory})});const E={clear:()=>{d.value=[]},submit:S,openOpenFileDialog:R};return Object.assign({mergedClsPrefix:o,draggerInsideRef:a,inputElRef:u,mergedTheme:i,dragOver:l,mergedMultiple:j,cssVars:r?void 0:y,themeClass:k==null?void 0:k.themeClass,onRender:k==null?void 0:k.onRender,handleFileInputChange:x},E)},render(){var e,o;const{draggerInsideRef:r,mergedClsPrefix:i,$slots:n,directory:s,onRender:d}=this;if(n.default&&!this.abstract){const u=n.default()[0];!((e=u==null?void 0:u.type)===null||e===void 0)&&e[pt]&&(r.value=!0)}const f=t("input",Object.assign({},this.inputProps,{ref:"inputElRef",type:"file",class:`${i}-upload-file-input`,accept:this.accept,multiple:this.mergedMultiple,onChange:this.handleFileInputChange,webkitdirectory:s||void 0,directory:s||void 0}));return this.abstract?t(Ce,null,(o=n.default)===null||o===void 0?void 0:o.call(n),t(Xt,{to:"body"},f)):(d==null||d(),t("div",{class:[`${i}-upload`,r.value&&`${i}-upload--dragger-inside`,this.dragOver&&`${i}-upload--drag-over`,this.themeClass],style:this.cssVars},f,this.showTrigger&&this.listType!=="image-card"&&t(wt,null,n),this.showFileList&&t(Mo,null,n)))}});export{Mo as _,Yo as a,wt as b};
