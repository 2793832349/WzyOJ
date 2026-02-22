import{i as P,o as W}from"./utils.83ed917f.1766986584207.js";import{t as N}from"./Tag.ff1efa14.1766986584207.js";import{$ as K,b as k,a_ as V,S as C,a$ as A,N as $,d as G,u as X,r as p,a1 as H,e as y,g as w,bp as q,a0 as D,h as U,j as Y,bq as J,F as Q,a8 as Z,am as ee,X as oe,k as R,ab as re,ad as te}from"./index.eb4377b0.1766986584207.js";const ne=K("n-avatar-group"),ae=k("avatar",`
 width: var(--n-merged-size);
 height: var(--n-merged-size);
 color: #FFF;
 font-size: var(--n-font-size);
 display: inline-flex;
 position: relative;
 overflow: hidden;
 text-align: center;
 border: var(--n-border);
 border-radius: var(--n-border-radius);
 --n-merged-color: var(--n-color);
 background-color: var(--n-merged-color);
 transition:
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier),
 color .3s var(--n-bezier);
`,[V(C("&","--n-merged-color: var(--n-color-modal);")),A(C("&","--n-merged-color: var(--n-color-popover);")),C("img",`
 width: 100%;
 height: 100%;
 `),$("text",`
 white-space: nowrap;
 display: inline-block;
 position: absolute;
 left: 50%;
 top: 50%;
 `),k("icon",`
 vertical-align: bottom;
 font-size: calc(var(--n-merged-size) - 6px);
 `),$("text","line-height: 1.25")]),se=Object.assign(Object.assign({},w.props),{size:[String,Number],src:String,circle:{type:Boolean,default:void 0},objectFit:String,round:{type:Boolean,default:void 0},bordered:{type:Boolean,default:void 0},onError:Function,fallbackSrc:String,intersectionObserverOptions:Object,lazy:Boolean,onLoad:Function,renderPlaceholder:Function,renderFallback:Function,imgProps:Object,color:String}),ce=G({name:"Avatar",props:se,setup(r){const{mergedClsPrefixRef:l,inlineThemeDisabled:h}=X(r),s=p(!1);let d=null;const m=p(null),i=p(null),L=()=>{const{value:e}=m;if(e&&(d===null||d!==e.innerHTML)){d=e.innerHTML;const{value:o}=i;if(o){const{offsetWidth:n,offsetHeight:t}=o,{offsetWidth:a,offsetHeight:F}=e,j=.9,O=Math.min(n/a*j,t/F*j,1);e.style.transform=`translateX(-50%) translateY(-50%) scale(${O})`}}},g=H(ne,null),b=y(()=>{const{size:e}=r;if(e)return e;const{size:o}=g||{};return o||"medium"}),x=w("Avatar","-avatar",ae,q,r,l),c=H(N,null),u=y(()=>{if(g)return!0;const{round:e,circle:o}=r;return e!==void 0||o!==void 0?e||o:c?c.roundRef.value:!1}),z=y(()=>g?!0:r.bordered||!1),f=e=>{var o;if(!S.value)return;s.value=!0;const{onError:n,imgProps:t}=r;(o=t==null?void 0:t.onError)===null||o===void 0||o.call(t,e),n&&n(e)};D(()=>r.src,()=>s.value=!1);const _=y(()=>{const e=b.value,o=u.value,n=z.value,{color:t}=r,{self:{borderRadius:a,fontSize:F,color:j,border:O,colorModal:B,colorPopover:I},common:{cubicBezierEaseInOut:M}}=x.value;let E;return typeof e=="number"?E=`${e}px`:E=x.value.self[U("height",e)],{"--n-font-size":F,"--n-border":n?O:"none","--n-border-radius":o?"50%":a,"--n-color":t||j,"--n-color-modal":t||B,"--n-color-popover":t||I,"--n-bezier":M,"--n-merged-size":`var(--n-avatar-size-override, ${E})`}}),v=h?Y("avatar",y(()=>{const e=b.value,o=u.value,n=z.value,{color:t}=r;let a="";return e&&(typeof e=="number"?a+=`a${e}`:a+=e[0]),o&&(a+="b"),n&&(a+="c"),t&&(a+=J(t)),a}),_,r):void 0,S=p(!r.lazy);Q(()=>{if(P)return;let e;const o=Z(()=>{e==null||e(),e=void 0,r.lazy&&(e=W(i.value,r.intersectionObserverOptions,S))});ee(()=>{o(),e==null||e()})});const T=p(!r.lazy);return{textRef:m,selfRef:i,mergedRoundRef:u,mergedClsPrefix:l,fitTextTransform:L,cssVars:h?void 0:_,themeClass:v==null?void 0:v.themeClass,onRender:v==null?void 0:v.onRender,hasLoadError:s,handleError:f,shouldStartLoading:S,loaded:T,mergedOnLoad:e=>{var o;const{onLoad:n,imgProps:t}=r;n==null||n(e),(o=t==null?void 0:t.onLoad)===null||o===void 0||o.call(t,e),T.value=!0}}},render(){var r,l;const{$slots:h,src:s,mergedClsPrefix:d,lazy:m,onRender:i,mergedOnLoad:L,shouldStartLoading:g,loaded:b,hasLoadError:x}=this;i==null||i();let c;const u=!b&&!x&&(this.renderPlaceholder?this.renderPlaceholder():(l=(r=this.$slots).placeholder)===null||l===void 0?void 0:l.call(r));return this.hasLoadError?c=this.renderFallback?this.renderFallback():oe(h.fallback,()=>[R("img",{src:this.fallbackSrc,style:{objectFit:this.objectFit}})]):c=re(h.default,z=>{if(z)return R(te,{onResize:this.fitTextTransform},{default:()=>R("span",{ref:"textRef",class:`${d}-avatar__text`},z)});if(s){const{imgProps:f}=this;return R("img",Object.assign(Object.assign({},f),{loading:P&&!this.intersectionObserverOptions&&m?"lazy":"eager",src:P||g||b?s:void 0,onLoad:L,"data-image-src":s,onError:this.handleError,style:[f==null?void 0:f.style,{objectFit:this.objectFit},u?{height:"0",width:"0",visibility:"hidden",position:"absolute"}:""]}))}}),R("span",{ref:"selfRef",class:[`${d}-avatar`,this.themeClass],style:this.cssVars},c,m&&u)}});export{ce as _};
