import{d as P,k as n,b as h,O as y,N as d,S as z,ca as j,u as D,r as H,e as N,a4 as M,g as T,a9 as V,aa as k,j as O,$ as W,cw as q,ai as I,cx as K,V as Y,p as Z,v as G,c9 as J,ap as Q,a6 as X,a1 as ee,bo as te,a2 as $,Y as ae,aU as re,cy as le}from"./index.eb4377b0.1766986584207.js";const ne=P({name:"ChevronLeft",render(){return n("svg",{viewBox:"0 0 16 16",fill:"none",xmlns:"http://www.w3.org/2000/svg"},n("path",{d:"M10.3536 3.14645C10.5488 3.34171 10.5488 3.65829 10.3536 3.85355L6.20711 8L10.3536 12.1464C10.5488 12.3417 10.5488 12.6583 10.3536 12.8536C10.1583 13.0488 9.84171 13.0488 9.64645 12.8536L5.14645 8.35355C4.95118 8.15829 4.95118 7.84171 5.14645 7.64645L9.64645 3.14645C9.84171 2.95118 10.1583 2.95118 10.3536 3.14645Z",fill:"currentColor"}))}}),oe=h("collapse","width: 100%;",[h("collapse-item",`
 font-size: var(--n-font-size);
 color: var(--n-text-color);
 transition:
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 margin: var(--n-item-margin);
 `,[y("disabled",[d("header","cursor: not-allowed;",[d("header-main",`
 color: var(--n-title-text-color-disabled);
 `),h("collapse-item-arrow",`
 color: var(--n-arrow-color-disabled);
 `)])]),h("collapse-item","margin-left: 32px;"),z("&:first-child","margin-top: 0;"),z("&:first-child >",[d("header","padding-top: 0;")]),y("left-arrow-placement",[d("header",[h("collapse-item-arrow","margin-right: 4px;")])]),y("right-arrow-placement",[d("header",[h("collapse-item-arrow","margin-left: 4px;")])]),d("content-wrapper",[d("content-inner","padding-top: 16px;"),j({duration:"0.15s"})]),y("active",[d("header",[y("active",[h("collapse-item-arrow","transform: rotate(90deg);")])])]),z("&:not(:first-child)","border-top: 1px solid var(--n-divider-color);"),d("header",`
 font-size: var(--n-title-font-size);
 display: flex;
 flex-wrap: nowrap;
 align-items: center;
 transition: color .3s var(--n-bezier);
 position: relative;
 padding: var(--n-title-padding);
 color: var(--n-title-text-color);
 cursor: pointer;
 `,[d("header-main",`
 display: flex;
 flex-wrap: nowrap;
 align-items: center;
 font-weight: var(--n-title-font-weight);
 transition: color .3s var(--n-bezier);
 flex: 1;
 color: var(--n-title-text-color);
 `),d("header-extra",`
 display: flex;
 align-items: center;
 transition: color .3s var(--n-bezier);
 color: var(--n-text-color);
 `),h("collapse-item-arrow",`
 display: flex;
 transition:
 transform .15s var(--n-bezier),
 color .3s var(--n-bezier);
 font-size: 18px;
 color: var(--n-arrow-color);
 `)])])]),se=Object.assign(Object.assign({},T.props),{defaultExpandedNames:{type:[Array,String],default:null},expandedNames:[Array,String],arrowPlacement:{type:String,default:"left"},accordion:{type:Boolean,default:!1},displayDirective:{type:String,default:"if"},onItemHeaderClick:[Function,Array],"onUpdate:expandedNames":[Function,Array],onUpdateExpandedNames:[Function,Array],onExpandedNamesChange:{type:[Function,Array],validator:()=>!0,default:void 0}}),A=W("n-collapse"),pe=P({name:"Collapse",props:se,setup(e,{slots:i}){const{mergedClsPrefixRef:o,inlineThemeDisabled:r,mergedRtlRef:c}=D(e),t=H(e.defaultExpandedNames),x=N(()=>e.expandedNames),u=M(x,t),g=T("Collapse","-collapse",oe,q,e,o);function p(m){const{"onUpdate:expandedNames":a,onUpdateExpandedNames:f,onExpandedNamesChange:w}=e;f&&I(f,m),a&&I(a,m),w&&I(w,m),t.value=m}function s(m){const{onItemHeaderClick:a}=e;a&&I(a,m)}function l(m,a,f){const{accordion:w}=e,{value:E}=u;if(w)m?(p([a]),s({name:a,expanded:!0,event:f})):(p([]),s({name:a,expanded:!1,event:f}));else if(!Array.isArray(E))p([a]),s({name:a,expanded:!0,event:f});else{const v=E.slice(),_=v.findIndex(S=>a===S);~_?(v.splice(_,1),p(v),s({name:a,expanded:!1,event:f})):(v.push(a),p(v),s({name:a,expanded:!0,event:f}))}}V(A,{props:e,mergedClsPrefixRef:o,expandedNamesRef:u,slots:i,toggleItem:l});const b=k("Collapse",c,o),R=N(()=>{const{common:{cubicBezierEaseInOut:m},self:{titleFontWeight:a,dividerColor:f,titlePadding:w,titleTextColor:E,titleTextColorDisabled:v,textColor:_,arrowColor:S,fontSize:F,titleFontSize:U,arrowColorDisabled:B,itemMargin:L}}=g.value;return{"--n-font-size":F,"--n-bezier":m,"--n-text-color":_,"--n-divider-color":f,"--n-title-padding":w,"--n-title-font-size":U,"--n-title-text-color":E,"--n-title-text-color-disabled":v,"--n-title-font-weight":a,"--n-arrow-color":S,"--n-arrow-color-disabled":B,"--n-item-margin":L}}),C=r?O("collapse",void 0,R,e):void 0;return{rtlEnabled:b,mergedTheme:g,mergedClsPrefix:o,cssVars:r?void 0:R,themeClass:C==null?void 0:C.themeClass,onRender:C==null?void 0:C.onRender}},render(){var e;return(e=this.onRender)===null||e===void 0||e.call(this),n("div",{class:[`${this.mergedClsPrefix}-collapse`,this.rtlEnabled&&`${this.mergedClsPrefix}-collapse--rtl`,this.themeClass],style:this.cssVars},this.$slots)}}),ie=P({name:"CollapseItemContent",props:{displayDirective:{type:String,required:!0},show:Boolean,clsPrefix:{type:String,required:!0}},setup(e){return{onceTrue:K(Y(e,"show"))}},render(){return n(J,null,{default:()=>{const{show:e,displayDirective:i,onceTrue:o,clsPrefix:r}=this,c=i==="show"&&o,t=n("div",{class:`${r}-collapse-item__content-wrapper`},n("div",{class:`${r}-collapse-item__content-inner`},this.$slots));return c?Z(t,[[G,e]]):e?t:null}})}}),de={title:String,name:[String,Number],disabled:Boolean,displayDirective:String},me=P({name:"CollapseItem",props:de,setup(e){const{mergedRtlRef:i}=D(e),o=Q(),r=X(()=>{var l;return(l=e.name)!==null&&l!==void 0?l:o}),c=ee(A);c||te("collapse-item","`n-collapse-item` must be placed inside `n-collapse`.");const{expandedNamesRef:t,props:x,mergedClsPrefixRef:u,slots:g}=c,p=N(()=>{const{value:l}=t;if(Array.isArray(l)){const{value:b}=r;return!~l.findIndex(R=>R===b)}else if(l){const{value:b}=r;return b!==l}return!0});return{rtlEnabled:k("Collapse",i,u),collapseSlots:g,randomName:o,mergedClsPrefix:u,collapsed:p,mergedDisplayDirective:N(()=>{const{displayDirective:l}=e;return l||x.displayDirective}),arrowPlacement:N(()=>x.arrowPlacement),handleClick(l){c&&!e.disabled&&c.toggleItem(p.value,r.value,l)}}},render(){const{collapseSlots:e,$slots:i,arrowPlacement:o,collapsed:r,mergedDisplayDirective:c,mergedClsPrefix:t,disabled:x}=this,u=$(i.header,{collapsed:r},()=>[this.title]),g=i["header-extra"]||e["header-extra"],p=i.arrow||e.arrow;return n("div",{class:[`${t}-collapse-item`,`${t}-collapse-item--${o}-arrow-placement`,x&&`${t}-collapse-item--disabled`,!r&&`${t}-collapse-item--active`]},n("div",{class:[`${t}-collapse-item__header`,!r&&`${t}-collapse-item__header--active`]},n("div",{class:`${t}-collapse-item__header-main`,onClick:this.handleClick},o==="right"&&u,n("div",{class:`${t}-collapse-item-arrow`,key:this.rtlEnabled?0:1},$(p,{collapsed:r},()=>{var s;return[n(ae,{clsPrefix:t},{default:(s=e.expandIcon)!==null&&s!==void 0?s:()=>this.rtlEnabled?n(ne,null):n(re,null)})]})),o==="left"&&u),le(g,{collapsed:r},s=>n("div",{class:`${t}-collapse-item__header-extra`,onClick:this.handleClick},s))),n(ie,{clsPrefix:t,displayDirective:c,show:!r},i))}});export{pe as _,me as a};
