import{d as de,b1 as pt,b2 as mt,F as ze,b3 as Ut,aP as Gt,e as I,r as C,a6 as Le,aR as tt,aT as Ne,k as d,aQ as qt,ad as at,b4 as De,aY as Yt,af as lt,b5 as Xt,b6 as st,am as wt,a1 as yt,b7 as it,b8 as xe,Y as Qt,ar as xt,b as P,N as j,O as ne,S as re,M as nt,aZ as St,g as Ce,V as J,b9 as Zt,ba as Jt,a0 as Se,h as be,ah as Xe,a9 as dt,bb as en,j as rt,ab as tn,Z as nn,ac as on,X as ln,aG as Ve,bc as rn,a8 as an,bd as sn,aK as dn,Q as un,u as cn,be as fn,a4 as ut,aF as hn,bf as vn,a5 as bn,bg as gn,aN as ot,bh as pn,bi as mn,bj as wn,p as yn,v as xn,bk as ct,bl as Sn,bm as Cn,ai as ie}from"./index.eb4377b0.1766986584207.js";import{u as Fn}from"./Eye.1e3444f4.1766986584207.js";import{N as Rn}from"./Input.4c626101.1766986584207.js";import{a as Tn,_ as Qe}from"./Tag.ff1efa14.1766986584207.js";function On(e){switch(typeof e){case"string":return e||void 0;case"number":return String(e);default:return}}function Ze(e){const n=e.filter(o=>o!==void 0);if(n.length!==0)return n.length===1?n[0]:o=>{e.forEach(i=>{i&&i(o)})}}function ft(e){return e&-e}class Mn{constructor(n,o){this.l=n,this.min=o;const i=new Array(n+1);for(let s=0;s<n+1;++s)i[s]=0;this.ft=i}add(n,o){if(o===0)return;const{l:i,ft:s}=this;for(n+=1;n<=i;)s[n]+=o,n+=ft(n)}get(n){return this.sum(n+1)-this.sum(n)}sum(n){if(n===void 0&&(n=this.l),n<=0)return 0;const{ft:o,min:i,l:s}=this;if(n>s)throw new Error("[FinweckTree.sum]: `i` is larger than length.");let v=n*i;for(;n>0;)v+=o[n],n-=ft(n);return v}getBound(n){let o=0,i=this.l;for(;i>o;){const s=Math.floor((o+i)/2),v=this.sum(s);if(v>n){i=s;continue}else if(v<n){if(o===s)return this.sum(o+1)<=n?o+1:s;o=s}else return s}return o}}let Ee;function kn(){return Ee===void 0&&("matchMedia"in window?Ee=window.matchMedia("(pointer:coarse)").matches:Ee=!1),Ee}let Je;function ht(){return Je===void 0&&(Je="chrome"in window?window.devicePixelRatio:1),Je}const zn=De(".v-vl",{maxHeight:"inherit",height:"100%",overflow:"auto",minWidth:"1px"},[De("&:not(.v-vl--show-scrollbar)",{scrollbarWidth:"none"},[De("&::-webkit-scrollbar, &::-webkit-scrollbar-track-piece, &::-webkit-scrollbar-thumb",{width:0,height:0,display:"none"})])]),Pn=de({name:"VirtualList",inheritAttrs:!1,props:{showScrollbar:{type:Boolean,default:!0},items:{type:Array,default:()=>[]},itemSize:{type:Number,required:!0},itemResizable:Boolean,itemsStyle:[String,Object],visibleItemsTag:{type:[String,Object],default:"div"},visibleItemsProps:Object,ignoreItemResize:Boolean,onScroll:Function,onWheel:Function,onResize:Function,defaultScrollKey:[Number,String],defaultScrollIndex:Number,keyField:{type:String,default:"key"},paddingTop:{type:[Number,String],default:0},paddingBottom:{type:[Number,String],default:0}},setup(e){const n=pt();zn.mount({id:"vueuc/virtual-list",head:!0,anchorMetaName:mt,ssr:n}),ze(()=>{const{defaultScrollIndex:f,defaultScrollKey:h}=e;f!=null?p({index:f}):h!=null&&p({key:h})});let o=!1,i=!1;Ut(()=>{if(o=!1,!i){i=!0;return}p({top:N.value,left:S})}),Gt(()=>{o=!0,i||(i=!0)});const s=I(()=>{const f=new Map,{keyField:h}=e;return e.items.forEach((k,V)=>{f.set(k[h],V)}),f}),v=C(null),g=C(void 0),a=new Map,R=I(()=>{const{items:f,itemSize:h,keyField:k}=e,V=new Mn(f.length,h);return f.forEach((W,L)=>{const _=W[k],H=a.get(_);H!==void 0&&V.add(L,H)}),V}),x=C(0);let S=0;const N=C(0),B=Le(()=>Math.max(R.value.getBound(N.value-tt(e.paddingTop))-1,0)),$=I(()=>{const{value:f}=g;if(f===void 0)return[];const{items:h,itemSize:k}=e,V=B.value,W=Math.min(V+Math.ceil(f/k+1),h.length-1),L=[];for(let _=V;_<=W;++_)L.push(h[_]);return L}),p=(f,h)=>{if(typeof f=="number"){m(f,h,"auto");return}const{left:k,top:V,index:W,key:L,position:_,behavior:H,debounce:l=!0}=f;if(k!==void 0||V!==void 0)m(k,V,H);else if(W!==void 0)y(W,H,l);else if(L!==void 0){const c=s.value.get(L);c!==void 0&&y(c,H,l)}else _==="bottom"?m(0,Number.MAX_SAFE_INTEGER,H):_==="top"&&m(0,0,H)};let F,D=null;function y(f,h,k){const{value:V}=R,W=V.sum(f)+tt(e.paddingTop);if(!k)v.value.scrollTo({left:0,top:W,behavior:h});else{F=f,D!==null&&window.clearTimeout(D),D=window.setTimeout(()=>{F=void 0,D=null},16);const{scrollTop:L,offsetHeight:_}=v.value;if(W>L){const H=V.get(f);W+H<=L+_||v.value.scrollTo({left:0,top:W+H-_,behavior:h})}else v.value.scrollTo({left:0,top:W,behavior:h})}}function m(f,h,k){v.value.scrollTo({left:f,top:h,behavior:k})}function U(f,h){var k,V,W;if(o||e.ignoreItemResize||ee(h.target))return;const{value:L}=R,_=s.value.get(f),H=L.get(_),l=(W=(V=(k=h.borderBoxSize)===null||k===void 0?void 0:k[0])===null||V===void 0?void 0:V.blockSize)!==null&&W!==void 0?W:h.contentRect.height;if(l===H)return;l-e.itemSize===0?a.delete(f):a.set(f,l-e.itemSize);const A=l-H;if(A===0)return;L.add(_,A);const Q=v.value;if(Q!=null){if(F===void 0){const ae=L.sum(_);Q.scrollTop>ae&&Q.scrollBy(0,A)}else if(_<F)Q.scrollBy(0,A);else if(_===F){const ae=L.sum(_);l+ae>Q.scrollTop+Q.offsetHeight&&Q.scrollBy(0,A)}le()}x.value++}const Y=!kn();let G=!1;function E(f){var h;(h=e.onScroll)===null||h===void 0||h.call(e,f),(!Y||!G)&&le()}function q(f){var h;if((h=e.onWheel)===null||h===void 0||h.call(e,f),Y){const k=v.value;if(k!=null){if(f.deltaX===0&&(k.scrollTop===0&&f.deltaY<=0||k.scrollTop+k.offsetHeight>=k.scrollHeight&&f.deltaY>=0))return;f.preventDefault(),k.scrollTop+=f.deltaY/ht(),k.scrollLeft+=f.deltaX/ht(),le(),G=!0,Yt(()=>{G=!1})}}}function Z(f){if(o||ee(f.target)||f.contentRect.height===g.value)return;g.value=f.contentRect.height;const{onResize:h}=e;h!==void 0&&h(f)}function le(){const{value:f}=v;f!=null&&(N.value=f.scrollTop,S=f.scrollLeft)}function ee(f){let h=f;for(;h!==null;){if(h.style.display==="none")return!0;h=h.parentElement}return!1}return{listHeight:g,listStyle:{overflow:"auto"},keyToIndex:s,itemsStyle:I(()=>{const{itemResizable:f}=e,h=Ne(R.value.sum());return x.value,[e.itemsStyle,{boxSizing:"content-box",height:f?"":h,minHeight:f?h:"",paddingTop:Ne(e.paddingTop),paddingBottom:Ne(e.paddingBottom)}]}),visibleItemsStyle:I(()=>(x.value,{transform:`translateY(${Ne(R.value.sum(B.value))})`})),viewportItems:$,listElRef:v,itemsElRef:C(null),scrollTo:p,handleListResize:Z,handleListScroll:E,handleListWheel:q,handleItemResize:U}},render(){const{itemResizable:e,keyField:n,keyToIndex:o,visibleItemsTag:i}=this;return d(at,{onResize:this.handleListResize},{default:()=>{var s,v;return d("div",qt(this.$attrs,{class:["v-vl",this.showScrollbar&&"v-vl--show-scrollbar"],onScroll:this.handleListScroll,onWheel:this.handleListWheel,ref:"listElRef"}),[this.items.length!==0?d("div",{ref:"itemsElRef",class:"v-vl-items",style:this.itemsStyle},[d(i,Object.assign({class:"v-vl-visible-items",style:this.visibleItemsStyle},this.visibleItemsProps),{default:()=>this.viewportItems.map(g=>{const a=g[n],R=o.get(a),x=this.$slots.default({item:g,index:R})[0];return e?d(at,{key:a,onResize:S=>this.handleItemResize(a,S)},{default:()=>x}):(x.key=a,x)})})]):(v=(s=this.$slots).empty)===null||v===void 0?void 0:v.call(s)])}})}}),ve="v-hidden",_n=De("[v-hidden]",{display:"none!important"}),vt=de({name:"Overflow",props:{getCounter:Function,getTail:Function,updateCounter:Function,onUpdateOverflow:Function},setup(e,{slots:n}){const o=C(null),i=C(null);function s(){const{value:g}=o,{getCounter:a,getTail:R}=e;let x;if(a!==void 0?x=a():x=i.value,!g||!x)return;x.hasAttribute(ve)&&x.removeAttribute(ve);const{children:S}=g,N=g.offsetWidth,B=[],$=n.tail?R==null?void 0:R():null;let p=$?$.offsetWidth:0,F=!1;const D=g.children.length-(n.tail?1:0);for(let m=0;m<D-1;++m){if(m<0)continue;const U=S[m];if(F){U.hasAttribute(ve)||U.setAttribute(ve,"");continue}else U.hasAttribute(ve)&&U.removeAttribute(ve);const Y=U.offsetWidth;if(p+=Y,B[m]=Y,p>N){const{updateCounter:G}=e;for(let E=m;E>=0;--E){const q=D-1-E;G!==void 0?G(q):x.textContent=`${q}`;const Z=x.offsetWidth;if(p-=B[E],p+Z<=N||E===0){F=!0,m=E-1,$&&(m===-1?($.style.maxWidth=`${N-Z}px`,$.style.boxSizing="border-box"):$.style.maxWidth="");break}}}}const{onUpdateOverflow:y}=e;F?y!==void 0&&y(!0):(y!==void 0&&y(!1),x.setAttribute(ve,""))}const v=pt();return _n.mount({id:"vueuc/overflow",head:!0,anchorMetaName:mt,ssr:v}),ze(s),{selfRef:o,counterRef:i,sync:s}},render(){const{$slots:e}=this;return lt(this.sync),d("div",{class:"v-overflow",ref:"selfRef"},[Xt(e,"default"),e.counter?e.counter():d("span",{style:{display:"inline-block"},ref:"counterRef"}),e.tail?e.tail():null])}});function Ct(e,n){n&&(ze(()=>{const{value:o}=e;o&&st.registerHandler(o,n)}),wt(()=>{const{value:o}=e;o&&st.unregisterHandler(o)}))}const In=de({name:"Checkmark",render(){return d("svg",{xmlns:"http://www.w3.org/2000/svg",viewBox:"0 0 16 16"},d("g",{fill:"none"},d("path",{d:"M14.046 3.486a.75.75 0 0 1-.032 1.06l-7.93 7.474a.85.85 0 0 1-1.188-.022l-2.68-2.72a.75.75 0 1 1 1.068-1.053l2.234 2.267l7.468-7.038a.75.75 0 0 1 1.06.032z",fill:"currentColor"})))}}),Bn=de({props:{onFocus:Function,onBlur:Function},setup(e){return()=>d("div",{style:"width: 0; height: 0",tabindex:0,onFocus:e.onFocus,onBlur:e.onBlur})}});function $n(e,n){return d(xt,{name:"fade-in-scale-up-transition"},{default:()=>e?d(Qt,{clsPrefix:n,class:`${n}-base-select-option__check`},{default:()=>d(In)}):null})}const bt=de({name:"NBaseSelectOption",props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(e){const{valueRef:n,pendingTmNodeRef:o,multipleRef:i,valueSetRef:s,renderLabelRef:v,renderOptionRef:g,labelFieldRef:a,valueFieldRef:R,showCheckmarkRef:x,nodePropsRef:S,handleOptionClick:N,handleOptionMouseEnter:B}=yt(it),$=Le(()=>{const{value:y}=o;return y?e.tmNode.key===y.key:!1});function p(y){const{tmNode:m}=e;m.disabled||N(y,m)}function F(y){const{tmNode:m}=e;m.disabled||B(y,m)}function D(y){const{tmNode:m}=e,{value:U}=$;m.disabled||U||B(y,m)}return{multiple:i,isGrouped:Le(()=>{const{tmNode:y}=e,{parent:m}=y;return m&&m.rawNode.type==="group"}),showCheckmark:x,nodeProps:S,isPending:$,isSelected:Le(()=>{const{value:y}=n,{value:m}=i;if(y===null)return!1;const U=e.tmNode.rawNode[R.value];if(m){const{value:Y}=s;return Y.has(U)}else return y===U}),labelField:a,renderLabel:v,renderOption:g,handleMouseMove:D,handleMouseEnter:F,handleClick:p}},render(){const{clsPrefix:e,tmNode:{rawNode:n},isSelected:o,isPending:i,isGrouped:s,showCheckmark:v,nodeProps:g,renderOption:a,renderLabel:R,handleClick:x,handleMouseEnter:S,handleMouseMove:N}=this,B=$n(o,e),$=R?[R(n,o),v&&B]:[xe(n[this.labelField],n,o),v&&B],p=g==null?void 0:g(n),F=d("div",Object.assign({},p,{class:[`${e}-base-select-option`,n.class,p==null?void 0:p.class,{[`${e}-base-select-option--disabled`]:n.disabled,[`${e}-base-select-option--selected`]:o,[`${e}-base-select-option--grouped`]:s,[`${e}-base-select-option--pending`]:i,[`${e}-base-select-option--show-checkmark`]:v}],style:[(p==null?void 0:p.style)||"",n.style||""],onClick:Ze([x,p==null?void 0:p.onClick]),onMouseenter:Ze([S,p==null?void 0:p.onMouseenter]),onMousemove:Ze([N,p==null?void 0:p.onMousemove])}),d("div",{class:`${e}-base-select-option__content`},$));return n.render?n.render({node:F,option:n,selected:o}):a?a({node:F,option:n,selected:o}):F}}),gt=de({name:"NBaseSelectGroupHeader",props:{clsPrefix:{type:String,required:!0},tmNode:{type:Object,required:!0}},setup(){const{renderLabelRef:e,renderOptionRef:n,labelFieldRef:o,nodePropsRef:i}=yt(it);return{labelField:o,nodeProps:i,renderLabel:e,renderOption:n}},render(){const{clsPrefix:e,renderLabel:n,renderOption:o,nodeProps:i,tmNode:{rawNode:s}}=this,v=i==null?void 0:i(s),g=n?n(s,!1):xe(s[this.labelField],s,!1),a=d("div",Object.assign({},v,{class:[`${e}-base-select-group-header`,v==null?void 0:v.class]}),g);return s.render?s.render({node:a,option:s}):o?o({node:a,option:s,selected:!1}):a}}),An=P("base-select-menu",`
 line-height: 1.5;
 outline: none;
 z-index: 0;
 position: relative;
 border-radius: var(--n-border-radius);
 transition:
 background-color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier);
 background-color: var(--n-color);
`,[P("scrollbar",`
 max-height: var(--n-height);
 `),P("virtual-list",`
 max-height: var(--n-height);
 `),P("base-select-option",`
 min-height: var(--n-option-height);
 font-size: var(--n-option-font-size);
 display: flex;
 align-items: center;
 `,[j("content",`
 z-index: 1;
 white-space: nowrap;
 text-overflow: ellipsis;
 overflow: hidden;
 `)]),P("base-select-group-header",`
 min-height: var(--n-option-height);
 font-size: .93em;
 display: flex;
 align-items: center;
 `),P("base-select-menu-option-wrapper",`
 position: relative;
 width: 100%;
 `),j("loading, empty",`
 display: flex;
 padding: 12px 32px;
 flex: 1;
 justify-content: center;
 `),j("loading",`
 color: var(--n-loading-color);
 font-size: var(--n-loading-size);
 `),j("action",`
 padding: 8px var(--n-option-padding-left);
 font-size: var(--n-option-font-size);
 transition: 
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 border-top: 1px solid var(--n-action-divider-color);
 color: var(--n-action-text-color);
 `),P("base-select-group-header",`
 position: relative;
 cursor: default;
 padding: var(--n-option-padding);
 color: var(--n-group-header-text-color);
 `),P("base-select-option",`
 cursor: pointer;
 position: relative;
 padding: var(--n-option-padding);
 transition:
 color .3s var(--n-bezier),
 opacity .3s var(--n-bezier);
 box-sizing: border-box;
 color: var(--n-option-text-color);
 opacity: 1;
 `,[ne("show-checkmark",`
 padding-right: calc(var(--n-option-padding-right) + 20px);
 `),re("&::before",`
 content: "";
 position: absolute;
 left: 4px;
 right: 4px;
 top: 0;
 bottom: 0;
 border-radius: var(--n-border-radius);
 transition: background-color .3s var(--n-bezier);
 `),re("&:active",`
 color: var(--n-option-text-color-pressed);
 `),ne("grouped",`
 padding-left: calc(var(--n-option-padding-left) * 1.5);
 `),ne("pending",[re("&::before",`
 background-color: var(--n-option-color-pending);
 `)]),ne("selected",`
 color: var(--n-option-text-color-active);
 `,[re("&::before",`
 background-color: var(--n-option-color-active);
 `),ne("pending",[re("&::before",`
 background-color: var(--n-option-color-active-pending);
 `)])]),ne("disabled",`
 cursor: not-allowed;
 `,[nt("selected",`
 color: var(--n-option-text-color-disabled);
 `),ne("selected",`
 opacity: var(--n-option-opacity-disabled);
 `)]),j("check",`
 font-size: 16px;
 position: absolute;
 right: calc(var(--n-option-padding-right) - 4px);
 top: calc(50% - 7px);
 color: var(--n-option-check-color);
 transition: color .3s var(--n-bezier);
 `,[St({enterScale:"0.5"})])])]),Nn=de({name:"InternalSelectMenu",props:Object.assign(Object.assign({},Ce.props),{clsPrefix:{type:String,required:!0},scrollable:{type:Boolean,default:!0},treeMate:{type:Object,required:!0},multiple:Boolean,size:{type:String,default:"medium"},value:{type:[String,Number,Array],default:null},autoPending:Boolean,virtualScroll:{type:Boolean,default:!0},show:{type:Boolean,default:!0},labelField:{type:String,default:"label"},valueField:{type:String,default:"value"},loading:Boolean,focusable:Boolean,renderLabel:Function,renderOption:Function,nodeProps:Function,showCheckmark:{type:Boolean,default:!0},onMousedown:Function,onScroll:Function,onFocus:Function,onBlur:Function,onKeyup:Function,onKeydown:Function,onTabOut:Function,onMouseenter:Function,onMouseleave:Function,onResize:Function,resetMenuOnOptionsChange:{type:Boolean,default:!0},inlineThemeDisabled:Boolean,onToggle:Function}),setup(e){const n=Ce("InternalSelectMenu","-internal-select-menu",An,Zt,e,J(e,"clsPrefix")),o=C(null),i=C(null),s=C(null),v=I(()=>e.treeMate.getFlattenedNodes()),g=I(()=>Jt(v.value)),a=C(null);function R(){const{treeMate:l}=e;let c=null;const{value:A}=e;A===null?c=l.getFirstAvailableNode():(e.multiple?c=l.getNode((A||[])[(A||[]).length-1]):c=l.getNode(A),(!c||c.disabled)&&(c=l.getFirstAvailableNode())),f(c||null)}function x(){const{value:l}=a;l&&!e.treeMate.getNode(l.key)&&(a.value=null)}let S;Se(()=>e.show,l=>{l?S=Se(()=>e.treeMate,()=>{e.resetMenuOnOptionsChange?(e.autoPending?R():x(),lt(h)):x()},{immediate:!0}):S==null||S()},{immediate:!0}),wt(()=>{S==null||S()});const N=I(()=>tt(n.value.self[be("optionHeight",e.size)])),B=I(()=>Xe(n.value.self[be("padding",e.size)])),$=I(()=>e.multiple&&Array.isArray(e.value)?new Set(e.value):new Set),p=I(()=>{const l=v.value;return l&&l.length===0});function F(l){const{onToggle:c}=e;c&&c(l)}function D(l){const{onScroll:c}=e;c&&c(l)}function y(l){var c;(c=s.value)===null||c===void 0||c.sync(),D(l)}function m(){var l;(l=s.value)===null||l===void 0||l.sync()}function U(){const{value:l}=a;return l||null}function Y(l,c){c.disabled||f(c,!1)}function G(l,c){c.disabled||F(c)}function E(l){var c;Ve(l,"action")||(c=e.onKeyup)===null||c===void 0||c.call(e,l)}function q(l){var c;Ve(l,"action")||(c=e.onKeydown)===null||c===void 0||c.call(e,l)}function Z(l){var c;(c=e.onMousedown)===null||c===void 0||c.call(e,l),!e.focusable&&l.preventDefault()}function le(){const{value:l}=a;l&&f(l.getNext({loop:!0}),!0)}function ee(){const{value:l}=a;l&&f(l.getPrev({loop:!0}),!0)}function f(l,c=!1){a.value=l,c&&h()}function h(){var l,c;const A=a.value;if(!A)return;const Q=g.value(A.key);Q!==null&&(e.virtualScroll?(l=i.value)===null||l===void 0||l.scrollTo({index:Q}):(c=s.value)===null||c===void 0||c.scrollTo({index:Q,elSize:N.value}))}function k(l){var c,A;!((c=o.value)===null||c===void 0)&&c.contains(l.target)&&((A=e.onFocus)===null||A===void 0||A.call(e,l))}function V(l){var c,A;!((c=o.value)===null||c===void 0)&&c.contains(l.relatedTarget)||(A=e.onBlur)===null||A===void 0||A.call(e,l)}dt(it,{handleOptionMouseEnter:Y,handleOptionClick:G,valueSetRef:$,pendingTmNodeRef:a,nodePropsRef:J(e,"nodeProps"),showCheckmarkRef:J(e,"showCheckmark"),multipleRef:J(e,"multiple"),valueRef:J(e,"value"),renderLabelRef:J(e,"renderLabel"),renderOptionRef:J(e,"renderOption"),labelFieldRef:J(e,"labelField"),valueFieldRef:J(e,"valueField")}),dt(en,o),ze(()=>{const{value:l}=s;l&&l.sync()});const W=I(()=>{const{size:l}=e,{common:{cubicBezierEaseInOut:c},self:{height:A,borderRadius:Q,color:ae,groupHeaderTextColor:Fe,actionDividerColor:Re,optionTextColorPressed:ge,optionTextColor:pe,optionTextColorDisabled:se,optionTextColorActive:te,optionOpacityDisabled:me,optionCheckColor:ue,actionTextColor:Te,optionColorPending:fe,optionColorActive:he,loadingColor:Oe,loadingSize:Me,optionColorActivePending:ke,[be("optionFontSize",l)]:we,[be("optionHeight",l)]:ye,[be("optionPadding",l)]:oe}}=n.value;return{"--n-height":A,"--n-action-divider-color":Re,"--n-action-text-color":Te,"--n-bezier":c,"--n-border-radius":Q,"--n-color":ae,"--n-option-font-size":we,"--n-group-header-text-color":Fe,"--n-option-check-color":ue,"--n-option-color-pending":fe,"--n-option-color-active":he,"--n-option-color-active-pending":ke,"--n-option-height":ye,"--n-option-opacity-disabled":me,"--n-option-text-color":pe,"--n-option-text-color-active":te,"--n-option-text-color-disabled":se,"--n-option-text-color-pressed":ge,"--n-option-padding":oe,"--n-option-padding-left":Xe(oe,"left"),"--n-option-padding-right":Xe(oe,"right"),"--n-loading-color":Oe,"--n-loading-size":Me}}),{inlineThemeDisabled:L}=e,_=L?rt("internal-select-menu",I(()=>e.size[0]),W,e):void 0,H={selfRef:o,next:le,prev:ee,getPendingTmNode:U};return Ct(o,e.onResize),Object.assign({mergedTheme:n,virtualListRef:i,scrollbarRef:s,itemSize:N,padding:B,flattenedNodes:v,empty:p,virtualListContainer(){const{value:l}=i;return l==null?void 0:l.listElRef},virtualListContent(){const{value:l}=i;return l==null?void 0:l.itemsElRef},doScroll:D,handleFocusin:k,handleFocusout:V,handleKeyUp:E,handleKeyDown:q,handleMouseDown:Z,handleVirtualListResize:m,handleVirtualListScroll:y,cssVars:L?void 0:W,themeClass:_==null?void 0:_.themeClass,onRender:_==null?void 0:_.onRender},H)},render(){const{$slots:e,virtualScroll:n,clsPrefix:o,mergedTheme:i,themeClass:s,onRender:v}=this;return v==null||v(),d("div",{ref:"selfRef",tabindex:this.focusable?0:-1,class:[`${o}-base-select-menu`,s,this.multiple&&`${o}-base-select-menu--multiple`],style:this.cssVars,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onKeyup:this.handleKeyUp,onKeydown:this.handleKeyDown,onMousedown:this.handleMouseDown,onMouseenter:this.onMouseenter,onMouseleave:this.onMouseleave},this.loading?d("div",{class:`${o}-base-select-menu__loading`},d(nn,{clsPrefix:o,strokeWidth:20})):this.empty?d("div",{class:`${o}-base-select-menu__empty`,"data-empty":!0},ln(e.empty,()=>[d(Tn,{theme:i.peers.Empty,themeOverrides:i.peerOverrides.Empty})])):d(on,{ref:"scrollbarRef",theme:i.peers.Scrollbar,themeOverrides:i.peerOverrides.Scrollbar,scrollable:this.scrollable,container:n?this.virtualListContainer:void 0,content:n?this.virtualListContent:void 0,onScroll:n?void 0:this.doScroll},{default:()=>n?d(Pn,{ref:"virtualListRef",class:`${o}-virtual-list`,items:this.flattenedNodes,itemSize:this.itemSize,showScrollbar:!1,paddingTop:this.padding.top,paddingBottom:this.padding.bottom,onResize:this.handleVirtualListResize,onScroll:this.handleVirtualListScroll,itemResizable:!0},{default:({item:g})=>g.isGroup?d(gt,{key:g.key,clsPrefix:o,tmNode:g}):g.ignored?null:d(bt,{clsPrefix:o,key:g.key,tmNode:g})}):d("div",{class:`${o}-base-select-menu-option-wrapper`,style:{paddingTop:this.padding.top,paddingBottom:this.padding.bottom}},this.flattenedNodes.map(g=>g.isGroup?d(gt,{key:g.key,clsPrefix:o,tmNode:g}):d(bt,{clsPrefix:o,key:g.key,tmNode:g})))}),tn(e.action,g=>g&&[d("div",{class:`${o}-base-select-menu__action`,"data-action":!0,key:"action"},g),d(Bn,{onFocus:this.onTabOut,key:"focus-detector"})]))}}),En=re([P("base-selection",`
 position: relative;
 z-index: auto;
 box-shadow: none;
 width: 100%;
 max-width: 100%;
 display: inline-block;
 vertical-align: bottom;
 border-radius: var(--n-border-radius);
 min-height: var(--n-height);
 line-height: 1.5;
 font-size: var(--n-font-size);
 `,[P("base-loading",`
 color: var(--n-loading-color);
 `),P("base-selection-tags","min-height: var(--n-height);"),j("border, state-border",`
 position: absolute;
 left: 0;
 right: 0;
 top: 0;
 bottom: 0;
 pointer-events: none;
 border: var(--n-border);
 border-radius: inherit;
 transition:
 box-shadow .3s var(--n-bezier),
 border-color .3s var(--n-bezier);
 `),j("state-border",`
 z-index: 1;
 border-color: #0000;
 `),P("base-suffix",`
 cursor: pointer;
 position: absolute;
 top: 50%;
 transform: translateY(-50%);
 right: 10px;
 `,[j("arrow",`
 font-size: var(--n-arrow-size);
 color: var(--n-arrow-color);
 transition: color .3s var(--n-bezier);
 `)]),P("base-selection-overlay",`
 display: flex;
 align-items: center;
 white-space: nowrap;
 pointer-events: none;
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 left: 0;
 padding: var(--n-padding-single);
 transition: color .3s var(--n-bezier);
 `,[j("wrapper",`
 flex-basis: 0;
 flex-grow: 1;
 overflow: hidden;
 text-overflow: ellipsis;
 `)]),P("base-selection-placeholder",`
 color: var(--n-placeholder-color);
 `,[j("inner",`
 max-width: 100%;
 overflow: hidden;
 `)]),P("base-selection-tags",`
 cursor: pointer;
 outline: none;
 box-sizing: border-box;
 position: relative;
 z-index: auto;
 display: flex;
 padding: var(--n-padding-multiple);
 flex-wrap: wrap;
 align-items: center;
 width: 100%;
 vertical-align: bottom;
 background-color: var(--n-color);
 border-radius: inherit;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 `),P("base-selection-label",`
 height: var(--n-height);
 display: inline-flex;
 width: 100%;
 vertical-align: bottom;
 cursor: pointer;
 outline: none;
 z-index: auto;
 box-sizing: border-box;
 position: relative;
 transition:
 color .3s var(--n-bezier),
 box-shadow .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 border-radius: inherit;
 background-color: var(--n-color);
 align-items: center;
 `,[P("base-selection-input",`
 font-size: inherit;
 line-height: inherit;
 outline: none;
 cursor: pointer;
 box-sizing: border-box;
 border:none;
 width: 100%;
 padding: var(--n-padding-single);
 background-color: #0000;
 color: var(--n-text-color);
 transition: color .3s var(--n-bezier);
 caret-color: var(--n-caret-color);
 `,[j("content",`
 text-overflow: ellipsis;
 overflow: hidden;
 white-space: nowrap; 
 `)]),j("render-label",`
 color: var(--n-text-color);
 `)]),nt("disabled",[re("&:hover",[j("state-border",`
 box-shadow: var(--n-box-shadow-hover);
 border: var(--n-border-hover);
 `)]),ne("focus",[j("state-border",`
 box-shadow: var(--n-box-shadow-focus);
 border: var(--n-border-focus);
 `)]),ne("active",[j("state-border",`
 box-shadow: var(--n-box-shadow-active);
 border: var(--n-border-active);
 `),P("base-selection-label","background-color: var(--n-color-active);"),P("base-selection-tags","background-color: var(--n-color-active);")])]),ne("disabled","cursor: not-allowed;",[j("arrow",`
 color: var(--n-arrow-color-disabled);
 `),P("base-selection-label",`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `,[P("base-selection-input",`
 cursor: not-allowed;
 color: var(--n-text-color-disabled);
 `),j("render-label",`
 color: var(--n-text-color-disabled);
 `)]),P("base-selection-tags",`
 cursor: not-allowed;
 background-color: var(--n-color-disabled);
 `),P("base-selection-placeholder",`
 cursor: not-allowed;
 color: var(--n-placeholder-color-disabled);
 `)]),P("base-selection-input-tag",`
 height: calc(var(--n-height) - 6px);
 line-height: calc(var(--n-height) - 6px);
 outline: none;
 display: none;
 position: relative;
 margin-bottom: 3px;
 max-width: 100%;
 vertical-align: bottom;
 `,[j("input",`
 font-size: inherit;
 font-family: inherit;
 min-width: 1px;
 padding: 0;
 background-color: #0000;
 outline: none;
 border: none;
 max-width: 100%;
 overflow: hidden;
 width: 1em;
 line-height: inherit;
 cursor: pointer;
 color: var(--n-text-color);
 caret-color: var(--n-caret-color);
 `),j("mirror",`
 position: absolute;
 left: 0;
 top: 0;
 white-space: pre;
 visibility: hidden;
 user-select: none;
 -webkit-user-select: none;
 opacity: 0;
 `)]),["warning","error"].map(e=>ne(`${e}-status`,[j("state-border",`border: var(--n-border-${e});`),nt("disabled",[re("&:hover",[j("state-border",`
 box-shadow: var(--n-box-shadow-hover-${e});
 border: var(--n-border-hover-${e});
 `)]),ne("active",[j("state-border",`
 box-shadow: var(--n-box-shadow-active-${e});
 border: var(--n-border-active-${e});
 `),P("base-selection-label",`background-color: var(--n-color-active-${e});`),P("base-selection-tags",`background-color: var(--n-color-active-${e});`)]),ne("focus",[j("state-border",`
 box-shadow: var(--n-box-shadow-focus-${e});
 border: var(--n-border-focus-${e});
 `)])])]))]),P("base-selection-popover",`
 margin-bottom: -3px;
 display: flex;
 flex-wrap: wrap;
 margin-right: -8px;
 `),P("base-selection-tag-wrapper",`
 max-width: 100%;
 display: inline-flex;
 padding: 0 7px 3px 0;
 `,[re("&:last-child","padding-right: 0;"),P("tag",`
 font-size: 14px;
 max-width: 100%;
 `,[j("content",`
 line-height: 1.25;
 text-overflow: ellipsis;
 overflow: hidden;
 `)])])]),Ln=de({name:"InternalSelection",props:Object.assign(Object.assign({},Ce.props),{clsPrefix:{type:String,required:!0},bordered:{type:Boolean,default:void 0},active:Boolean,pattern:{type:String,default:""},placeholder:String,selectedOption:{type:Object,default:null},selectedOptions:{type:Array,default:null},labelField:{type:String,default:"label"},valueField:{type:String,default:"value"},multiple:Boolean,filterable:Boolean,clearable:Boolean,disabled:Boolean,size:{type:String,default:"medium"},loading:Boolean,autofocus:Boolean,showArrow:{type:Boolean,default:!0},inputProps:Object,focused:Boolean,renderTag:Function,onKeydown:Function,onClick:Function,onBlur:Function,onFocus:Function,onDeleteOption:Function,maxTagCount:[String,Number],onClear:Function,onPatternInput:Function,onPatternFocus:Function,onPatternBlur:Function,renderLabel:Function,status:String,inlineThemeDisabled:Boolean,ignoreComposition:{type:Boolean,default:!0},onResize:Function}),setup(e){const n=C(null),o=C(null),i=C(null),s=C(null),v=C(null),g=C(null),a=C(null),R=C(null),x=C(null),S=C(null),N=C(!1),B=C(!1),$=C(!1),p=Ce("InternalSelection","-internal-selection",En,rn,e,J(e,"clsPrefix")),F=I(()=>e.clearable&&!e.disabled&&($.value||e.active)),D=I(()=>e.selectedOption?e.renderTag?e.renderTag({option:e.selectedOption,handleClose:()=>{}}):e.renderLabel?e.renderLabel(e.selectedOption,!0):xe(e.selectedOption[e.labelField],e.selectedOption,!0):e.placeholder),y=I(()=>{const r=e.selectedOption;if(!!r)return r[e.labelField]}),m=I(()=>e.multiple?!!(Array.isArray(e.selectedOptions)&&e.selectedOptions.length):e.selectedOption!==null);function U(){var r;const{value:b}=n;if(b){const{value:K}=o;K&&(K.style.width=`${b.offsetWidth}px`,e.maxTagCount!=="responsive"&&((r=x.value)===null||r===void 0||r.sync()))}}function Y(){const{value:r}=S;r&&(r.style.display="none")}function G(){const{value:r}=S;r&&(r.style.display="inline-block")}Se(J(e,"active"),r=>{r||Y()}),Se(J(e,"pattern"),()=>{e.multiple&&lt(U)});function E(r){const{onFocus:b}=e;b&&b(r)}function q(r){const{onBlur:b}=e;b&&b(r)}function Z(r){const{onDeleteOption:b}=e;b&&b(r)}function le(r){const{onClear:b}=e;b&&b(r)}function ee(r){const{onPatternInput:b}=e;b&&b(r)}function f(r){var b;(!r.relatedTarget||!(!((b=i.value)===null||b===void 0)&&b.contains(r.relatedTarget)))&&E(r)}function h(r){var b;!((b=i.value)===null||b===void 0)&&b.contains(r.relatedTarget)||q(r)}function k(r){le(r)}function V(){$.value=!0}function W(){$.value=!1}function L(r){!e.active||!e.filterable||r.target!==o.value&&r.preventDefault()}function _(r){Z(r)}function H(r){if(r.key==="Backspace"&&!l.value&&!e.pattern.length){const{selectedOptions:b}=e;b!=null&&b.length&&_(b[b.length-1])}}const l=C(!1);let c=null;function A(r){const{value:b}=n;if(b){const K=r.target.value;b.textContent=K,U()}e.ignoreComposition&&l.value?c=r:ee(r)}function Q(){l.value=!0}function ae(){l.value=!1,e.ignoreComposition&&ee(c),c=null}function Fe(r){var b;B.value=!0,(b=e.onPatternFocus)===null||b===void 0||b.call(e,r)}function Re(r){var b;B.value=!1,(b=e.onPatternBlur)===null||b===void 0||b.call(e,r)}function ge(){var r,b;if(e.filterable)B.value=!1,(r=g.value)===null||r===void 0||r.blur(),(b=o.value)===null||b===void 0||b.blur();else if(e.multiple){const{value:K}=s;K==null||K.blur()}else{const{value:K}=v;K==null||K.blur()}}function pe(){var r,b,K;e.filterable?(B.value=!1,(r=g.value)===null||r===void 0||r.focus()):e.multiple?(b=s.value)===null||b===void 0||b.focus():(K=v.value)===null||K===void 0||K.focus()}function se(){const{value:r}=o;r&&(G(),r.focus())}function te(){const{value:r}=o;r&&r.blur()}function me(r){const{value:b}=a;b&&b.setTextContent(`+${r}`)}function ue(){const{value:r}=R;return r}function Te(){return o.value}let fe=null;function he(){fe!==null&&window.clearTimeout(fe)}function Oe(){e.disabled||e.active||(he(),fe=window.setTimeout(()=>{m.value&&(N.value=!0)},100))}function Me(){he()}function ke(r){r||(he(),N.value=!1)}Se(m,r=>{r||(N.value=!1)}),ze(()=>{an(()=>{const r=g.value;!r||(r.tabIndex=e.disabled||B.value?-1:0)})}),Ct(i,e.onResize);const{inlineThemeDisabled:we}=e,ye=I(()=>{const{size:r}=e,{common:{cubicBezierEaseInOut:b},self:{borderRadius:K,color:Pe,placeholderColor:je,textColor:He,paddingSingle:Ke,paddingMultiple:Ue,caretColor:_e,colorDisabled:Ie,textColorDisabled:Be,placeholderColorDisabled:Ge,colorActive:qe,boxShadowFocus:$e,boxShadowActive:ce,boxShadowHover:t,border:u,borderFocus:w,borderHover:z,borderActive:T,arrowColor:M,arrowColorDisabled:O,loadingColor:X,colorActiveWarning:Ae,boxShadowFocusWarning:Ye,boxShadowActiveWarning:Rt,boxShadowHoverWarning:Tt,borderWarning:Ot,borderFocusWarning:Mt,borderHoverWarning:kt,borderActiveWarning:zt,colorActiveError:Pt,boxShadowFocusError:_t,boxShadowActiveError:It,boxShadowHoverError:Bt,borderError:$t,borderFocusError:At,borderHoverError:Nt,borderActiveError:Et,clearColor:Lt,clearColorHover:Dt,clearColorPressed:Vt,clearSize:Wt,arrowSize:jt,[be("height",r)]:Ht,[be("fontSize",r)]:Kt}}=p.value;return{"--n-bezier":b,"--n-border":u,"--n-border-active":T,"--n-border-focus":w,"--n-border-hover":z,"--n-border-radius":K,"--n-box-shadow-active":ce,"--n-box-shadow-focus":$e,"--n-box-shadow-hover":t,"--n-caret-color":_e,"--n-color":Pe,"--n-color-active":qe,"--n-color-disabled":Ie,"--n-font-size":Kt,"--n-height":Ht,"--n-padding-single":Ke,"--n-padding-multiple":Ue,"--n-placeholder-color":je,"--n-placeholder-color-disabled":Ge,"--n-text-color":He,"--n-text-color-disabled":Be,"--n-arrow-color":M,"--n-arrow-color-disabled":O,"--n-loading-color":X,"--n-color-active-warning":Ae,"--n-box-shadow-focus-warning":Ye,"--n-box-shadow-active-warning":Rt,"--n-box-shadow-hover-warning":Tt,"--n-border-warning":Ot,"--n-border-focus-warning":Mt,"--n-border-hover-warning":kt,"--n-border-active-warning":zt,"--n-color-active-error":Pt,"--n-box-shadow-focus-error":_t,"--n-box-shadow-active-error":It,"--n-box-shadow-hover-error":Bt,"--n-border-error":$t,"--n-border-focus-error":At,"--n-border-hover-error":Nt,"--n-border-active-error":Et,"--n-clear-size":Wt,"--n-clear-color":Lt,"--n-clear-color-hover":Dt,"--n-clear-color-pressed":Vt,"--n-arrow-size":jt}}),oe=we?rt("internal-selection",I(()=>e.size[0]),ye,e):void 0;return{mergedTheme:p,mergedClearable:F,patternInputFocused:B,filterablePlaceholder:D,label:y,selected:m,showTagsPanel:N,isComposing:l,counterRef:a,counterWrapperRef:R,patternInputMirrorRef:n,patternInputRef:o,selfRef:i,multipleElRef:s,singleElRef:v,patternInputWrapperRef:g,overflowRef:x,inputTagElRef:S,handleMouseDown:L,handleFocusin:f,handleClear:k,handleMouseEnter:V,handleMouseLeave:W,handleDeleteOption:_,handlePatternKeyDown:H,handlePatternInputInput:A,handlePatternInputBlur:Re,handlePatternInputFocus:Fe,handleMouseEnterCounter:Oe,handleMouseLeaveCounter:Me,handleFocusout:h,handleCompositionEnd:ae,handleCompositionStart:Q,onPopoverUpdateShow:ke,focus:pe,focusInput:se,blur:ge,blurInput:te,updateCounter:me,getCounter:ue,getTail:Te,renderLabel:e.renderLabel,cssVars:we?void 0:ye,themeClass:oe==null?void 0:oe.themeClass,onRender:oe==null?void 0:oe.onRender}},render(){const{status:e,multiple:n,size:o,disabled:i,filterable:s,maxTagCount:v,bordered:g,clsPrefix:a,onRender:R,renderTag:x,renderLabel:S}=this;R==null||R();const N=v==="responsive",B=typeof v=="number",$=N||B,p=d(sn,null,{default:()=>d(Rn,{clsPrefix:a,loading:this.loading,showArrow:this.showArrow,showClear:this.mergedClearable&&this.selected,onClear:this.handleClear},{default:()=>{var D,y;return(y=(D=this.$slots).arrow)===null||y===void 0?void 0:y.call(D)}})});let F;if(n){const{labelField:D}=this,y=h=>d("div",{class:`${a}-base-selection-tag-wrapper`,key:h.value},x?x({option:h,handleClose:()=>{this.handleDeleteOption(h)}}):d(Qe,{size:o,closable:!h.disabled,disabled:i,onClose:()=>{this.handleDeleteOption(h)},internalCloseIsButtonTag:!1,internalCloseFocusable:!1},{default:()=>S?S(h,!0):xe(h[D],h,!0)})),m=()=>(B?this.selectedOptions.slice(0,v):this.selectedOptions).map(y),U=s?d("div",{class:`${a}-base-selection-input-tag`,ref:"inputTagElRef",key:"__input-tag__"},d("input",Object.assign({},this.inputProps,{ref:"patternInputRef",tabindex:-1,disabled:i,value:this.pattern,autofocus:this.autofocus,class:`${a}-base-selection-input-tag__input`,onBlur:this.handlePatternInputBlur,onFocus:this.handlePatternInputFocus,onKeydown:this.handlePatternKeyDown,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),d("span",{ref:"patternInputMirrorRef",class:`${a}-base-selection-input-tag__mirror`},this.pattern)):null,Y=N?()=>d("div",{class:`${a}-base-selection-tag-wrapper`,ref:"counterWrapperRef"},d(Qe,{size:o,ref:"counterRef",onMouseenter:this.handleMouseEnterCounter,onMouseleave:this.handleMouseLeaveCounter,disabled:i})):void 0;let G;if(B){const h=this.selectedOptions.length-v;h>0&&(G=d("div",{class:`${a}-base-selection-tag-wrapper`,key:"__counter__"},d(Qe,{size:o,ref:"counterRef",onMouseenter:this.handleMouseEnterCounter,disabled:i},{default:()=>`+${h}`})))}const E=N?s?d(vt,{ref:"overflowRef",updateCounter:this.updateCounter,getCounter:this.getCounter,getTail:this.getTail,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:m,counter:Y,tail:()=>U}):d(vt,{ref:"overflowRef",updateCounter:this.updateCounter,getCounter:this.getCounter,style:{width:"100%",display:"flex",overflow:"hidden"}},{default:m,counter:Y}):B?m().concat(G):m(),q=$?()=>d("div",{class:`${a}-base-selection-popover`},N?m():this.selectedOptions.map(y)):void 0,Z=$?{show:this.showTagsPanel,trigger:"hover",overlap:!0,placement:"top",width:"trigger",onUpdateShow:this.onPopoverUpdateShow,theme:this.mergedTheme.peers.Popover,themeOverrides:this.mergedTheme.peerOverrides.Popover}:null,ee=(this.selected?!1:this.active?!this.pattern&&!this.isComposing:!0)?d("div",{class:`${a}-base-selection-placeholder ${a}-base-selection-overlay`},d("div",{class:`${a}-base-selection-placeholder__inner`},this.placeholder)):null,f=s?d("div",{ref:"patternInputWrapperRef",class:`${a}-base-selection-tags`},E,N?null:U,p):d("div",{ref:"multipleElRef",class:`${a}-base-selection-tags`,tabindex:i?void 0:0},E,p);F=d(un,null,$?d(dn,Object.assign({},Z,{scrollable:!0,style:"max-height: calc(var(--v-target-height) * 6.6);"}),{trigger:()=>f,default:q}):f,ee)}else if(s){const D=this.pattern||this.isComposing,y=this.active?!D:!this.selected,m=this.active?!1:this.selected;F=d("div",{ref:"patternInputWrapperRef",class:`${a}-base-selection-label`},d("input",Object.assign({},this.inputProps,{ref:"patternInputRef",class:`${a}-base-selection-input`,value:this.active?this.pattern:"",placeholder:"",readonly:i,disabled:i,tabindex:-1,autofocus:this.autofocus,onFocus:this.handlePatternInputFocus,onBlur:this.handlePatternInputBlur,onInput:this.handlePatternInputInput,onCompositionstart:this.handleCompositionStart,onCompositionend:this.handleCompositionEnd})),m?d("div",{class:`${a}-base-selection-label__render-label ${a}-base-selection-overlay`,key:"input"},d("div",{class:`${a}-base-selection-overlay__wrapper`},x?x({option:this.selectedOption,handleClose:()=>{}}):S?S(this.selectedOption,!0):xe(this.label,this.selectedOption,!0))):null,y?d("div",{class:`${a}-base-selection-placeholder ${a}-base-selection-overlay`,key:"placeholder"},d("div",{class:`${a}-base-selection-overlay__wrapper`},this.filterablePlaceholder)):null,p)}else F=d("div",{ref:"singleElRef",class:`${a}-base-selection-label`,tabindex:this.disabled?void 0:0},this.label!==void 0?d("div",{class:`${a}-base-selection-input`,title:On(this.label),key:"input"},d("div",{class:`${a}-base-selection-input__content`},x?x({option:this.selectedOption,handleClose:()=>{}}):S?S(this.selectedOption,!0):xe(this.label,this.selectedOption,!0))):d("div",{class:`${a}-base-selection-placeholder ${a}-base-selection-overlay`,key:"placeholder"},d("div",{class:`${a}-base-selection-placeholder__inner`},this.placeholder)),p);return d("div",{ref:"selfRef",class:[`${a}-base-selection`,this.themeClass,e&&`${a}-base-selection--${e}-status`,{[`${a}-base-selection--active`]:this.active,[`${a}-base-selection--selected`]:this.selected||this.active&&this.pattern,[`${a}-base-selection--disabled`]:this.disabled,[`${a}-base-selection--multiple`]:this.multiple,[`${a}-base-selection--focus`]:this.focused}],style:this.cssVars,onClick:this.onClick,onMouseenter:this.handleMouseEnter,onMouseleave:this.handleMouseLeave,onKeydown:this.onKeydown,onFocusin:this.handleFocusin,onFocusout:this.handleFocusout,onMousedown:this.handleMouseDown},F,g?d("div",{class:`${a}-base-selection__border`}):null,g?d("div",{class:`${a}-base-selection__state-border`}):null)}});function We(e){return e.type==="group"}function Ft(e){return e.type==="ignored"}function et(e,n){try{return!!(1+n.toString().toLowerCase().indexOf(e.trim().toLowerCase()))}catch{return!1}}function Dn(e,n){return{getIsGroup:We,getIgnored:Ft,getKey(i){return We(i)?i.name||i.key||"key-required":i[e]},getChildren(i){return i[n]}}}function Vn(e,n,o,i){if(!n)return e;function s(v){if(!Array.isArray(v))return[];const g=[];for(const a of v)if(We(a)){const R=s(a[i]);R.length&&g.push(Object.assign({},a,{[i]:R}))}else{if(Ft(a))continue;n(o,a)&&g.push(a)}return g}return s(e)}function Wn(e,n,o){const i=new Map;return e.forEach(s=>{We(s)?s[o].forEach(v=>{i.set(v[n],v)}):i.set(s[n],s)}),i}const jn=re([P("select",`
 z-index: auto;
 outline: none;
 width: 100%;
 position: relative;
 `),P("select-menu",`
 margin: 4px 0;
 box-shadow: var(--n-menu-box-shadow);
 `,[St({originalTransition:"background-color .3s var(--n-bezier), box-shadow .3s var(--n-bezier)"})])]),Hn=Object.assign(Object.assign({},Ce.props),{to:ot.propTo,bordered:{type:Boolean,default:void 0},clearable:Boolean,clearFilterAfterSelect:{type:Boolean,default:!0},options:{type:Array,default:()=>[]},defaultValue:{type:[String,Number,Array],default:null},keyboard:{type:Boolean,default:!0},value:[String,Number,Array],placeholder:String,menuProps:Object,multiple:Boolean,size:String,filterable:Boolean,disabled:{type:Boolean,default:void 0},remote:Boolean,loading:Boolean,filter:Function,placement:{type:String,default:"bottom-start"},widthMode:{type:String,default:"trigger"},tag:Boolean,onCreate:Function,fallbackOption:{type:[Function,Boolean],default:void 0},show:{type:Boolean,default:void 0},showArrow:{type:Boolean,default:!0},maxTagCount:[Number,String],consistentMenuWidth:{type:Boolean,default:!0},virtualScroll:{type:Boolean,default:!0},labelField:{type:String,default:"label"},valueField:{type:String,default:"value"},childrenField:{type:String,default:"children"},renderLabel:Function,renderOption:Function,renderTag:Function,"onUpdate:value":[Function,Array],inputProps:Object,nodeProps:Function,ignoreComposition:{type:Boolean,default:!0},showOnFocus:Boolean,onUpdateValue:[Function,Array],onBlur:[Function,Array],onClear:[Function,Array],onFocus:[Function,Array],onScroll:[Function,Array],onSearch:[Function,Array],onUpdateShow:[Function,Array],"onUpdate:show":[Function,Array],displayDirective:{type:String,default:"show"},resetMenuOnOptionsChange:{type:Boolean,default:!0},status:String,showCheckmark:{type:Boolean,default:!0},onChange:[Function,Array],items:Array}),Yn=de({name:"Select",props:Hn,setup(e){const{mergedClsPrefixRef:n,mergedBorderedRef:o,namespaceRef:i,inlineThemeDisabled:s}=cn(e),v=Ce("Select","-select",jn,fn,e,n),g=C(e.defaultValue),a=J(e,"value"),R=ut(a,g),x=C(!1),S=C(""),N=I(()=>{const{valueField:t,childrenField:u}=e,w=Dn(t,u);return hn(h.value,w)}),B=I(()=>Wn(ee.value,e.valueField,e.childrenField)),$=C(!1),p=ut(J(e,"show"),$),F=C(null),D=C(null),y=C(null),{localeRef:m}=Fn("Select"),U=I(()=>{var t;return(t=e.placeholder)!==null&&t!==void 0?t:m.value.placeholder}),Y=vn(e,["items","options"]),G=[],E=C([]),q=C([]),Z=C(new Map),le=I(()=>{const{fallbackOption:t}=e;if(t===void 0){const{labelField:u,valueField:w}=e;return z=>({[u]:String(z),[w]:z})}return t===!1?!1:u=>Object.assign(t(u),{value:u})}),ee=I(()=>q.value.concat(E.value).concat(Y.value)),f=I(()=>{const{filter:t}=e;if(t)return t;const{labelField:u,valueField:w}=e;return(z,T)=>{if(!T)return!1;const M=T[u];if(typeof M=="string")return et(z,M);const O=T[w];return typeof O=="string"?et(z,O):typeof O=="number"?et(z,String(O)):!1}}),h=I(()=>{if(e.remote)return Y.value;{const{value:t}=ee,{value:u}=S;return!u.length||!e.filterable?t:Vn(t,f.value,u,e.childrenField)}});function k(t){const u=e.remote,{value:w}=Z,{value:z}=B,{value:T}=le,M=[];return t.forEach(O=>{if(z.has(O))M.push(z.get(O));else if(u&&w.has(O))M.push(w.get(O));else if(T){const X=T(O);X&&M.push(X)}}),M}const V=I(()=>{if(e.multiple){const{value:t}=R;return Array.isArray(t)?k(t):[]}return null}),W=I(()=>{const{value:t}=R;return!e.multiple&&!Array.isArray(t)?t===null?null:k([t])[0]||null:null}),L=bn(e),{mergedSizeRef:_,mergedDisabledRef:H,mergedStatusRef:l}=L;function c(t,u){const{onChange:w,"onUpdate:value":z,onUpdateValue:T}=e,{nTriggerFormChange:M,nTriggerFormInput:O}=L;w&&ie(w,t,u),T&&ie(T,t,u),z&&ie(z,t,u),g.value=t,M(),O()}function A(t){const{onBlur:u}=e,{nTriggerFormBlur:w}=L;u&&ie(u,t),w()}function Q(){const{onClear:t}=e;t&&ie(t)}function ae(t){const{onFocus:u,showOnFocus:w}=e,{nTriggerFormFocus:z}=L;u&&ie(u,t),z(),w&&se()}function Fe(t){const{onSearch:u}=e;u&&ie(u,t)}function Re(t){const{onScroll:u}=e;u&&ie(u,t)}function ge(){var t;const{remote:u,multiple:w}=e;if(u){const{value:z}=Z;if(w){const{valueField:T}=e;(t=V.value)===null||t===void 0||t.forEach(M=>{z.set(M[T],M)})}else{const T=W.value;T&&z.set(T[e.valueField],T)}}}function pe(t){const{onUpdateShow:u,"onUpdate:show":w}=e;u&&ie(u,t),w&&ie(w,t),$.value=t}function se(){H.value||(pe(!0),$.value=!0,e.filterable&&Be())}function te(){pe(!1)}function me(){S.value="",q.value=G}const ue=C(!1);function Te(){e.filterable&&(ue.value=!0)}function fe(){e.filterable&&(ue.value=!1,p.value||me())}function he(){H.value||(p.value?e.filterable?Be():te():se())}function Oe(t){var u,w;!((w=(u=y.value)===null||u===void 0?void 0:u.selfRef)===null||w===void 0)&&w.contains(t.relatedTarget)||(x.value=!1,A(t),te())}function Me(t){ae(t),x.value=!0}function ke(t){x.value=!0}function we(t){var u;!((u=F.value)===null||u===void 0)&&u.$el.contains(t.relatedTarget)||(x.value=!1,A(t),te())}function ye(){var t;(t=F.value)===null||t===void 0||t.focus(),te()}function oe(t){var u;p.value&&(!((u=F.value)===null||u===void 0)&&u.$el.contains(Sn(t))||te())}function r(t){if(!Array.isArray(t))return[];if(le.value)return Array.from(t);{const{remote:u}=e,{value:w}=B;if(u){const{value:z}=Z;return t.filter(T=>w.has(T)||z.has(T))}else return t.filter(z=>w.has(z))}}function b(t){K(t.rawNode)}function K(t){if(H.value)return;const{tag:u,remote:w,clearFilterAfterSelect:z,valueField:T}=e;if(u&&!w){const{value:M}=q,O=M[0]||null;if(O){const X=E.value;X.length?X.push(O):E.value=[O],q.value=G}}if(w&&Z.value.set(t[T],t),e.multiple){const M=r(R.value),O=M.findIndex(X=>X===t[T]);if(~O){if(M.splice(O,1),u&&!w){const X=Pe(t[T]);~X&&(E.value.splice(X,1),z&&(S.value=""))}}else M.push(t[T]),z&&(S.value="");c(M,k(M))}else{if(u&&!w){const M=Pe(t[T]);~M?E.value=[E.value[M]]:E.value=G}Ie(),te(),c(t[T],t)}}function Pe(t){return E.value.findIndex(w=>w[e.valueField]===t)}function je(t){p.value||se();const{value:u}=t.target;S.value=u;const{tag:w,remote:z}=e;if(Fe(u),w&&!z){if(!u){q.value=G;return}const{onCreate:T}=e,M=T?T(u):{[e.labelField]:u,[e.valueField]:u},{valueField:O}=e;Y.value.some(X=>X[O]===M[O])||E.value.some(X=>X[O]===M[O])?q.value=G:q.value=[M]}}function He(t){t.stopPropagation();const{multiple:u}=e;!u&&e.filterable&&te(),Q(),u?c([],[]):c(null,null)}function Ke(t){!Ve(t,"action")&&!Ve(t,"empty")&&t.preventDefault()}function Ue(t){Re(t)}function _e(t){var u,w,z,T,M;if(!e.keyboard){t.preventDefault();return}switch(t.key){case" ":if(e.filterable)break;t.preventDefault();case"Enter":if(!(!((u=F.value)===null||u===void 0)&&u.isComposing)){if(p.value){const O=(w=y.value)===null||w===void 0?void 0:w.getPendingTmNode();O?b(O):e.filterable||(te(),Ie())}else if(se(),e.tag&&ue.value){const O=q.value[0];if(O){const X=O[e.valueField],{value:Ae}=R;e.multiple&&Array.isArray(Ae)&&Ae.some(Ye=>Ye===X)||K(O)}}}t.preventDefault();break;case"ArrowUp":if(t.preventDefault(),e.loading)return;p.value&&((z=y.value)===null||z===void 0||z.prev());break;case"ArrowDown":if(t.preventDefault(),e.loading)return;p.value?(T=y.value)===null||T===void 0||T.next():se();break;case"Escape":p.value&&(Cn(t),te()),(M=F.value)===null||M===void 0||M.focus();break}}function Ie(){var t;(t=F.value)===null||t===void 0||t.focus()}function Be(){var t;(t=F.value)===null||t===void 0||t.focusInput()}function Ge(){var t;!p.value||(t=D.value)===null||t===void 0||t.syncPosition()}ge(),Se(J(e,"options"),ge);const qe={focus:()=>{var t;(t=F.value)===null||t===void 0||t.focus()},blur:()=>{var t;(t=F.value)===null||t===void 0||t.blur()}},$e=I(()=>{const{self:{menuBoxShadow:t}}=v.value;return{"--n-menu-box-shadow":t}}),ce=s?rt("select",void 0,$e,e):void 0;return Object.assign(Object.assign({},qe),{mergedStatus:l,mergedClsPrefix:n,mergedBordered:o,namespace:i,treeMate:N,isMounted:gn(),triggerRef:F,menuRef:y,pattern:S,uncontrolledShow:$,mergedShow:p,adjustedTo:ot(e),uncontrolledValue:g,mergedValue:R,followerRef:D,localizedPlaceholder:U,selectedOption:W,selectedOptions:V,mergedSize:_,mergedDisabled:H,focused:x,activeWithoutMenuOpen:ue,inlineThemeDisabled:s,onTriggerInputFocus:Te,onTriggerInputBlur:fe,handleTriggerOrMenuResize:Ge,handleMenuFocus:ke,handleMenuBlur:we,handleMenuTabOut:ye,handleTriggerClick:he,handleToggle:b,handleDeleteOption:K,handlePatternInput:je,handleClear:He,handleTriggerBlur:Oe,handleTriggerFocus:Me,handleKeydown:_e,handleMenuAfterLeave:me,handleMenuClickOutside:oe,handleMenuScroll:Ue,handleMenuKeydown:_e,handleMenuMousedown:Ke,mergedTheme:v,cssVars:s?void 0:$e,themeClass:ce==null?void 0:ce.themeClass,onRender:ce==null?void 0:ce.onRender})},render(){return d("div",{class:`${this.mergedClsPrefix}-select`},d(pn,null,{default:()=>[d(mn,null,{default:()=>d(Ln,{ref:"triggerRef",inlineThemeDisabled:this.inlineThemeDisabled,status:this.mergedStatus,inputProps:this.inputProps,clsPrefix:this.mergedClsPrefix,showArrow:this.showArrow,maxTagCount:this.maxTagCount,bordered:this.mergedBordered,active:this.activeWithoutMenuOpen||this.mergedShow,pattern:this.pattern,placeholder:this.localizedPlaceholder,selectedOption:this.selectedOption,selectedOptions:this.selectedOptions,multiple:this.multiple,renderTag:this.renderTag,renderLabel:this.renderLabel,filterable:this.filterable,clearable:this.clearable,disabled:this.mergedDisabled,size:this.mergedSize,theme:this.mergedTheme.peers.InternalSelection,labelField:this.labelField,valueField:this.valueField,themeOverrides:this.mergedTheme.peerOverrides.InternalSelection,loading:this.loading,focused:this.focused,onClick:this.handleTriggerClick,onDeleteOption:this.handleDeleteOption,onPatternInput:this.handlePatternInput,onClear:this.handleClear,onBlur:this.handleTriggerBlur,onFocus:this.handleTriggerFocus,onKeydown:this.handleKeydown,onPatternBlur:this.onTriggerInputBlur,onPatternFocus:this.onTriggerInputFocus,onResize:this.handleTriggerOrMenuResize,ignoreComposition:this.ignoreComposition},{arrow:()=>{var e,n;return[(n=(e=this.$slots).arrow)===null||n===void 0?void 0:n.call(e)]}})}),d(wn,{ref:"followerRef",show:this.mergedShow,to:this.adjustedTo,teleportDisabled:this.adjustedTo===ot.tdkey,containerClass:this.namespace,width:this.consistentMenuWidth?"target":void 0,minWidth:"target",placement:this.placement},{default:()=>d(xt,{name:"fade-in-scale-up-transition",appear:this.isMounted,onAfterLeave:this.handleMenuAfterLeave},{default:()=>{var e,n,o;return this.mergedShow||this.displayDirective==="show"?((e=this.onRender)===null||e===void 0||e.call(this),yn(d(Nn,Object.assign({},this.menuProps,{ref:"menuRef",onResize:this.handleTriggerOrMenuResize,inlineThemeDisabled:this.inlineThemeDisabled,virtualScroll:this.consistentMenuWidth&&this.virtualScroll,class:[`${this.mergedClsPrefix}-select-menu`,this.themeClass,(n=this.menuProps)===null||n===void 0?void 0:n.class],clsPrefix:this.mergedClsPrefix,focusable:!0,labelField:this.labelField,valueField:this.valueField,autoPending:!0,nodeProps:this.nodeProps,theme:this.mergedTheme.peers.InternalSelectMenu,themeOverrides:this.mergedTheme.peerOverrides.InternalSelectMenu,treeMate:this.treeMate,multiple:this.multiple,size:"medium",renderOption:this.renderOption,renderLabel:this.renderLabel,value:this.mergedValue,style:[(o=this.menuProps)===null||o===void 0?void 0:o.style,this.cssVars],onToggle:this.handleToggle,onScroll:this.handleMenuScroll,onFocus:this.handleMenuFocus,onBlur:this.handleMenuBlur,onKeydown:this.handleMenuKeydown,onTabOut:this.handleMenuTabOut,onMousedown:this.handleMenuMousedown,show:this.mergedShow,showCheckmark:this.showCheckmark,resetMenuOnOptionsChange:this.resetMenuOnOptionsChange}),{empty:()=>{var i,s;return[(s=(i=this.$slots).empty)===null||s===void 0?void 0:s.call(i)]},action:()=>{var i,s;return[(s=(i=this.$slots).action)===null||s===void 0?void 0:s.call(i)]}}),this.displayDirective==="show"?[[xn,this.mergedShow],[ct,this.handleMenuClickOutside,void 0,{capture:!0}]]:[[ct,this.handleMenuClickOutside,void 0,{capture:!0}]])):null}})})]}))}});export{Bn as F,Nn as N,Pn as V,Yn as _,Dn as c,On as g,Ze as m};
