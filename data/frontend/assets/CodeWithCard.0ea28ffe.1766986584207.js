import{a1 as M,ax as V,e as m,c as F,S as _,b as O,O as C,N as I,d as q,u as D,r as K,F as U,a0 as $,V as x,g as N,j as A,k as p,o as G,l as J,w,n as y,m as Q,_ as X}from"./index.eb4377b0.1766986584207.js";import{_ as Y}from"./Scrollbar.be2baf78.1766986584207.js";function Z(n,e){const o=M(V,null);return m(()=>n.hljs||(o==null?void 0:o.mergedHljsRef.value))}const ee=n=>{const{textColor2:e,fontSize:o,fontWeightStrong:c,textColor3:i}=n;return{textColor:e,fontSize:o,fontWeightStrong:c,"mono-3":"#a0a1a7","hue-1":"#0184bb","hue-2":"#4078f2","hue-3":"#a626a4","hue-4":"#50a14f","hue-5":"#e45649","hue-5-2":"#c91243","hue-6":"#986801","hue-6-2":"#c18401",lineNumberTextColor:i}},ne={name:"Code",common:F,self:ee},te=ne,oe=_([O("code",`
 font-size: var(--n-font-size);
 font-family: var(--n-font-family);
 `,[C("show-line-numbers",`
 display: flex;
 `),I("line-numbers",`
 user-select: none;
 padding-right: 12px;
 text-align: right;
 transition: color .3s var(--n-bezier);
 color: var(--n-line-number-text-color);
 `),C("word-wrap",[_("pre",`
 white-space: pre-wrap;
 word-break: break-all;
 `)]),_("pre",`
 margin: 0;
 line-height: inherit;
 font-size: inherit;
 font-family: inherit;
 `),_("[class^=hljs]",`
 color: var(--n-text-color);
 transition: 
 color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `)]),({props:n})=>{const e=`${n.bPrefix}code`;return[`${e} .hljs-comment,
 ${e} .hljs-quote {
 color: var(--n-mono-3);
 font-style: italic;
 }`,`${e} .hljs-doctag,
 ${e} .hljs-keyword,
 ${e} .hljs-formula {
 color: var(--n-hue-3);
 }`,`${e} .hljs-section,
 ${e} .hljs-name,
 ${e} .hljs-selector-tag,
 ${e} .hljs-deletion,
 ${e} .hljs-subst {
 color: var(--n-hue-5);
 }`,`${e} .hljs-literal {
 color: var(--n-hue-1);
 }`,`${e} .hljs-string,
 ${e} .hljs-regexp,
 ${e} .hljs-addition,
 ${e} .hljs-attribute,
 ${e} .hljs-meta-string {
 color: var(--n-hue-4);
 }`,`${e} .hljs-built_in,
 ${e} .hljs-class .hljs-title {
 color: var(--n-hue-6-2);
 }`,`${e} .hljs-attr,
 ${e} .hljs-variable,
 ${e} .hljs-template-variable,
 ${e} .hljs-type,
 ${e} .hljs-selector-class,
 ${e} .hljs-selector-attr,
 ${e} .hljs-selector-pseudo,
 ${e} .hljs-number {
 color: var(--n-hue-6);
 }`,`${e} .hljs-symbol,
 ${e} .hljs-bullet,
 ${e} .hljs-link,
 ${e} .hljs-meta,
 ${e} .hljs-selector-id,
 ${e} .hljs-title {
 color: var(--n-hue-2);
 }`,`${e} .hljs-emphasis {
 font-style: italic;
 }`,`${e} .hljs-strong {
 font-weight: var(--n-font-weight-strong);
 }`,`${e} .hljs-link {
 text-decoration: underline;
 }`]}]),le=Object.assign(Object.assign({},N.props),{language:String,code:{type:String,default:""},trim:{type:Boolean,default:!0},hljs:Object,uri:Boolean,inline:Boolean,wordWrap:Boolean,showLineNumbers:Boolean,internalFontSize:Number,internalNoHighlight:Boolean}),se=q({name:"Code",props:le,setup(n,{slots:e}){const{internalNoHighlight:o}=n,{mergedClsPrefixRef:c,inlineThemeDisabled:i}=D(),u=K(null),j=o?{value:void 0}:Z(n),S=(t,s,l)=>{const{value:r}=j;return!r||!(t&&r.getLanguage(t))?null:r.highlight(l?s.trim():s,{language:t}).value},z=m(()=>n.inline||n.wordWrap?!1:n.showLineNumbers),f=()=>{if(e.default)return;const{value:t}=u;if(!t)return;const{language:s}=n,l=n.uri?window.decodeURIComponent(n.code):n.code;if(s){const a=S(s,l,n.trim);if(a!==null){if(n.inline)t.innerHTML=a;else{const g=t.querySelector(".__code__");g&&t.removeChild(g);const d=document.createElement("pre");d.className="__code__",d.innerHTML=a,t.appendChild(d)}return}}if(n.inline){t.textContent=l;return}const r=t.querySelector(".__code__");if(r)r.textContent=l;else{const a=document.createElement("pre");a.className="__code__",a.textContent=l,t.innerHTML="",t.appendChild(a)}};U(f),$(x(n,"language"),f),$(x(n,"code"),f),o||$(j,f);const R=N("Code","-code",oe,te,n,c),b=m(()=>{const{common:{cubicBezierEaseInOut:t,fontFamilyMono:s},self:{textColor:l,fontSize:r,fontWeightStrong:a,lineNumberTextColor:g,"mono-3":d,"hue-1":L,"hue-2":B,"hue-3":H,"hue-4":k,"hue-5":P,"hue-5-2":E,"hue-6":T,"hue-6-2":W}}=R.value,{internalFontSize:v}=n;return{"--n-font-size":v?`${v}px`:r,"--n-font-family":s,"--n-font-weight-strong":a,"--n-bezier":t,"--n-text-color":l,"--n-mono-3":d,"--n-hue-1":L,"--n-hue-2":B,"--n-hue-3":H,"--n-hue-4":k,"--n-hue-5":P,"--n-hue-5-2":E,"--n-hue-6":T,"--n-hue-6-2":W,"--n-line-number-text-color":g}}),h=i?A("code",m(()=>`${n.internalFontSize||"a"}`),b,n):void 0;return{mergedClsPrefix:c,codeRef:u,mergedShowLineNumbers:z,lineNumbers:m(()=>{let t=1;const s=[];let l=!1;for(const r of n.code)r===`
`?(l=!0,s.push(t++)):l=!1;return l||s.push(t++),s.join(`
`)}),cssVars:i?void 0:b,themeClass:h==null?void 0:h.themeClass,onRender:h==null?void 0:h.onRender}},render(){var n,e;const{mergedClsPrefix:o,wordWrap:c,mergedShowLineNumbers:i,onRender:u}=this;return u==null||u(),p("code",{class:[`${o}-code`,this.themeClass,c&&`${o}-code--word-wrap`,i&&`${o}-code--show-line-numbers`],style:this.cssVars,ref:"codeRef"},i?p("pre",{class:`${o}-code__line-numbers`},this.lineNumbers):null,(e=(n=this.$slots).default)===null||e===void 0?void 0:e.call(n))}}),re={style:{"padding-bottom":"10px"}},ce={__name:"CodeWithCard",props:{code:{type:String,default:""}},setup(n){return(e,o)=>{const c=se,i=Y,u=X;return G(),J(u,null,{default:w(()=>[y(i,{"x-scrollable":"",style:{"margin-bottom":"-10px"}},{default:w(()=>[Q("div",re,[y(c,{code:n.code},null,8,["code"])])]),_:1})]),_:1})}}};export{ce as _,se as a};
