import{b as a,O as _,N as l,S as E,d as L,k as n,Y as ee,aU as te,g as V,a1 as oe,bB as re,r as N,e as P,f as Y,a4 as le,V as D,bC as ae,a9 as ne,bD as se,u as X,bE as ie,j as q,ac as ce,bF as de,ai as F,bG as ue,aa as be,ab as A,ay as pe,z as ge,bH as fe,o as j,l as M,w as u,A as me,aC as ve,n as g,m as C,t as x,G as U,L as H,C as y,J as K,s as he,bI as _e,Q as xe,E as ye,aA as Ce,aK as Se,bJ as ze,bK as Te}from"./index.eb4377b0.1766986584207.js";import{d as we}from"./consts.72579ead.1766986584207.js";import{S as ke}from"./SubmissionTable.534df1c8.1766986584207.js";import{_ as Re}from"./Time.2d3501e9.1766986584207.js";import{_ as $e}from"./LayoutContent.6fc7b93d.1766986584207.js";import"./utils.2f0dea37.1766986584207.js";import"./DataTable.8d4e61d5.1766986584207.js";import"./ArrowDown.1ae467bd.1766986584207.js";import"./Checkbox.7ca0c7f4.1766986584207.js";import"./RadioGroup.668f9840.1766986584207.js";import"./Input.4c626101.1766986584207.js";import"./Eye.1e3444f4.1766986584207.js";import"./Tooltip.2d4fe76d.1766986584207.js";import"./Select.324054db.1766986584207.js";import"./Tag.ff1efa14.1766986584207.js";import"./Forward.bac4cf6f.1766986584207.js";import"./Spin.3ae5ee7d.1766986584207.js";import"./index.225da447.1766986584207.js";const Be=a("layout-sider",`
 flex-shrink: 0;
 box-sizing: border-box;
 position: relative;
 z-index: 1;
 color: var(--n-text-color);
 transition:
 color .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 min-width .3s var(--n-bezier),
 max-width .3s var(--n-bezier),
 transform .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 background-color: var(--n-color);
 display: flex;
 justify-content: flex-end;
`,[_("bordered",[l("border",`
 content: "";
 position: absolute;
 top: 0;
 bottom: 0;
 width: 1px;
 background-color: var(--n-border-color);
 transition: background-color .3s var(--n-bezier);
 `)]),l("left-placement",[_("bordered",[l("border",`
 right: 0;
 `)])]),_("right-placement",`
 justify-content: flex-start;
 `,[_("bordered",[l("border",`
 left: 0;
 `)]),_("collapsed",[a("layout-toggle-button",[a("base-icon",`
 transform: rotate(180deg);
 `)]),a("layout-toggle-bar",[E("&:hover",[l("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),l("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])])]),a("layout-toggle-button",`
 left: 0;
 transform: translateX(-50%) translateY(-50%);
 `,[a("base-icon",`
 transform: rotate(0);
 `)]),a("layout-toggle-bar",`
 left: -28px;
 transform: rotate(180deg);
 `,[E("&:hover",[l("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),l("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})])])]),_("collapsed",[a("layout-toggle-bar",[E("&:hover",[l("top",{transform:"rotate(-12deg) scale(1.15) translateY(-2px)"}),l("bottom",{transform:"rotate(12deg) scale(1.15) translateY(2px)"})])]),a("layout-toggle-button",[a("base-icon",`
 transform: rotate(0);
 `)])]),a("layout-toggle-button",`
 transition:
 color .3s var(--n-bezier),
 right .3s var(--n-bezier),
 left .3s var(--n-bezier),
 border-color .3s var(--n-bezier),
 background-color .3s var(--n-bezier);
 cursor: pointer;
 width: 24px;
 height: 24px;
 position: absolute;
 top: 50%;
 right: 0;
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 18px;
 color: var(--n-toggle-button-icon-color);
 border: var(--n-toggle-button-border);
 background-color: var(--n-toggle-button-color);
 box-shadow: 0 2px 4px 0px rgba(0, 0, 0, .06);
 transform: translateX(50%) translateY(-50%);
 z-index: 1;
 `,[a("base-icon",`
 transition: transform .3s var(--n-bezier);
 transform: rotate(180deg);
 `)]),a("layout-toggle-bar",`
 cursor: pointer;
 height: 72px;
 width: 32px;
 position: absolute;
 top: calc(50% - 36px);
 right: -28px;
 `,[l("top, bottom",`
 position: absolute;
 width: 4px;
 border-radius: 2px;
 height: 38px;
 left: 14px;
 transition: 
 background-color .3s var(--n-bezier),
 transform .3s var(--n-bezier);
 `),l("bottom",`
 position: absolute;
 top: 34px;
 `),E("&:hover",[l("top",{transform:"rotate(12deg) scale(1.15) translateY(-2px)"}),l("bottom",{transform:"rotate(-12deg) scale(1.15) translateY(2px)"})]),l("top, bottom",{backgroundColor:"var(--n-toggle-bar-color)"}),E("&:hover",[l("top, bottom",{backgroundColor:"var(--n-toggle-bar-color-hover)"})])]),l("border",`
 position: absolute;
 top: 0;
 right: 0;
 bottom: 0;
 width: 1px;
 transition: background-color .3s var(--n-bezier);
 `),a("layout-sider-scroll-container",`
 flex-grow: 1;
 flex-shrink: 0;
 box-sizing: border-box;
 height: 100%;
 opacity: 0;
 transition: opacity .3s var(--n-bezier);
 max-width: 100%;
 `),_("show-content",[a("layout-sider-scroll-container",{opacity:1})]),_("absolute-positioned",`
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 `)]),Pe=L({name:"LayoutToggleButton",props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return n("div",{class:`${e}-layout-toggle-button`,onClick:this.onClick},n(ee,{clsPrefix:e},{default:()=>n(te,null)}))}}),Ie=L({props:{clsPrefix:{type:String,required:!0},onClick:Function},render(){const{clsPrefix:e}=this;return n("div",{onClick:this.onClick,class:`${e}-layout-toggle-bar`},n("div",{class:`${e}-layout-toggle-bar__top`}),n("div",{class:`${e}-layout-toggle-bar__bottom`}))}}),Ee={position:de,bordered:Boolean,collapsedWidth:{type:Number,default:48},width:{type:[Number,String],default:272},contentStyle:{type:[String,Object],default:""},collapseMode:{type:String,default:"transform"},collapsed:{type:Boolean,default:void 0},defaultCollapsed:Boolean,showCollapsedContent:{type:Boolean,default:!0},showTrigger:{type:[Boolean,String],default:!1},nativeScrollbar:{type:Boolean,default:!0},inverted:Boolean,scrollbarProps:Object,triggerStyle:[String,Object],collapsedTriggerStyle:[String,Object],"onUpdate:collapsed":[Function,Array],onUpdateCollapsed:[Function,Array],onAfterEnter:Function,onAfterLeave:Function,onExpand:[Function,Array],onCollapse:[Function,Array],onScroll:Function},je=L({name:"LayoutSider",props:Object.assign(Object.assign({},V.props),Ee),setup(e){const t=oe(re),c=N(null),r=N(null),v=P(()=>Y(f.value?e.collapsedWidth:e.width)),h=P(()=>e.collapseMode!=="transform"?{}:{minWidth:Y(e.width)}),d=P(()=>t?t.siderPlacement:"left"),b=N(e.defaultCollapsed),f=le(D(e,"collapsed"),b);function S(i,o){if(e.nativeScrollbar){const{value:s}=c;s&&(o===void 0?s.scrollTo(i):s.scrollTo(i,o))}else{const{value:s}=r;s&&s.scrollTo(i,o)}}function z(){const{"onUpdate:collapsed":i,onUpdateCollapsed:o,onExpand:s,onCollapse:O}=e,{value:B}=f;o&&F(o,!B),i&&F(i,!B),b.value=!B,B?s&&F(s):O&&F(O)}let T=0,w=0;const I=i=>{var o;const s=i.target;T=s.scrollLeft,w=s.scrollTop,(o=e.onScroll)===null||o===void 0||o.call(e,i)};ae(()=>{if(e.nativeScrollbar){const i=c.value;i&&(i.scrollTop=w,i.scrollLeft=T)}}),ne(se,{collapsedRef:f,collapseModeRef:D(e,"collapseMode")});const{mergedClsPrefixRef:k,inlineThemeDisabled:R}=X(e),p=V("Layout","-layout-sider",Be,ie,e,k);function J(i){var o,s;i.propertyName==="max-width"&&(f.value?(o=e.onAfterLeave)===null||o===void 0||o.call(e):(s=e.onAfterEnter)===null||s===void 0||s.call(e))}const Q={scrollTo:S},W=P(()=>{const{common:{cubicBezierEaseInOut:i},self:o}=p.value,{siderToggleButtonColor:s,siderToggleButtonBorder:O,siderToggleBarColor:B,siderToggleBarColorHover:Z}=o,m={"--n-bezier":i,"--n-toggle-button-color":s,"--n-toggle-button-border":O,"--n-toggle-bar-color":B,"--n-toggle-bar-color-hover":Z};return e.inverted?(m["--n-color"]=o.siderColorInverted,m["--n-text-color"]=o.textColorInverted,m["--n-border-color"]=o.siderBorderColorInverted,m["--n-toggle-button-icon-color"]=o.siderToggleButtonIconColorInverted,m.__invertScrollbar=o.__invertScrollbar):(m["--n-color"]=o.siderColor,m["--n-text-color"]=o.textColor,m["--n-border-color"]=o.siderBorderColor,m["--n-toggle-button-icon-color"]=o.siderToggleButtonIconColor),m}),$=R?q("layout-sider",P(()=>e.inverted?"a":"b"),W,e):void 0;return Object.assign({scrollableElRef:c,scrollbarInstRef:r,mergedClsPrefix:k,mergedTheme:p,styleMaxWidth:v,mergedCollapsed:f,scrollContainerStyle:h,siderPlacement:d,handleNativeElScroll:I,handleTransitionend:J,handleTriggerClick:z,inlineThemeDisabled:R,cssVars:W,themeClass:$==null?void 0:$.themeClass,onRender:$==null?void 0:$.onRender},Q)},render(){var e;const{mergedClsPrefix:t,mergedCollapsed:c,showTrigger:r}=this;return(e=this.onRender)===null||e===void 0||e.call(this),n("aside",{class:[`${t}-layout-sider`,this.themeClass,`${t}-layout-sider--${this.position}-positioned`,`${t}-layout-sider--${this.siderPlacement}-placement`,this.bordered&&`${t}-layout-sider--bordered`,c&&`${t}-layout-sider--collapsed`,(!c||this.showCollapsedContent)&&`${t}-layout-sider--show-content`],onTransitionend:this.handleTransitionend,style:[this.inlineThemeDisabled?void 0:this.cssVars,{maxWidth:this.styleMaxWidth,width:Y(this.width)}]},this.nativeScrollbar?n("div",{class:`${t}-layout-sider-scroll-container`,onScroll:this.handleNativeElScroll,style:[this.scrollContainerStyle,{overflow:"auto"},this.contentStyle],ref:"scrollableElRef"},this.$slots):n(ce,Object.assign({},this.scrollbarProps,{onScroll:this.onScroll,ref:"scrollbarInstRef",style:this.scrollContainerStyle,contentStyle:this.contentStyle,theme:this.mergedTheme.peers.Scrollbar,themeOverrides:this.mergedTheme.peerOverrides.Scrollbar,builtinThemeOverrides:this.inverted&&this.cssVars.__invertScrollbar==="true"?{colorHover:"rgba(255, 255, 255, .4)",color:"rgba(255, 255, 255, .3)"}:void 0}),this.$slots),r?r==="bar"?n(Ie,{clsPrefix:t,style:c?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):n(Pe,{clsPrefix:t,style:c?this.collapsedTriggerStyle:this.triggerStyle,onClick:this.handleTriggerClick}):null,this.bordered?n("div",{class:`${t}-layout-sider__border`}):null)}}),Ne=a("statistic",[l("label",`
 font-weight: var(--n-label-font-weight);
 transition: .3s color var(--n-bezier);
 font-size: var(--n-label-font-size);
 color: var(--n-label-text-color);
 `),a("statistic-value",`
 margin-top: 4px;
 font-weight: var(--n-value-font-weight);
 `,[l("prefix",`
 margin: 0 4px 0 0;
 font-size: var(--n-value-font-size);
 transition: .3s color var(--n-bezier);
 color: var(--n-value-prefix-text-color);
 `,[a("icon",{verticalAlign:"-0.125em"})]),l("content",`
 font-size: var(--n-value-font-size);
 transition: .3s color var(--n-bezier);
 color: var(--n-value-text-color);
 `),l("suffix",`
 margin: 0 0 0 4px;
 font-size: var(--n-value-font-size);
 transition: .3s color var(--n-bezier);
 color: var(--n-value-suffix-text-color);
 `,[a("icon",{verticalAlign:"-0.125em"})])])]),Oe=Object.assign(Object.assign({},V.props),{tabularNums:Boolean,label:String,value:[String,Number]}),Fe=L({name:"Statistic",props:Oe,setup(e){const{mergedClsPrefixRef:t,inlineThemeDisabled:c,mergedRtlRef:r}=X(e),v=V("Statistic","-statistic",Ne,ue,e,t),h=be("Statistic",r,t),d=P(()=>{const{self:{labelFontWeight:f,valueFontSize:S,valueFontWeight:z,valuePrefixTextColor:T,labelTextColor:w,valueSuffixTextColor:I,valueTextColor:k,labelFontSize:R},common:{cubicBezierEaseInOut:p}}=v.value;return{"--n-bezier":p,"--n-label-font-size":R,"--n-label-font-weight":f,"--n-label-text-color":w,"--n-value-font-weight":z,"--n-value-font-size":S,"--n-value-prefix-text-color":T,"--n-value-suffix-text-color":I,"--n-value-text-color":k}}),b=c?q("statistic",void 0,d,e):void 0;return{rtlEnabled:h,mergedClsPrefix:t,cssVars:c?void 0:d,themeClass:b==null?void 0:b.themeClass,onRender:b==null?void 0:b.onRender}},render(){var e;const{mergedClsPrefix:t,$slots:{default:c,label:r,prefix:v,suffix:h}}=this;return(e=this.onRender)===null||e===void 0||e.call(this),n("div",{class:[`${t}-statistic`,this.themeClass,this.rtlEnabled&&`${t}-statistic--rtl`],style:this.cssVars},A(r,d=>n("div",{class:`${t}-statistic__label`},this.label||d)),n("div",{class:`${t}-statistic-value`,style:{fontVariantNumeric:this.tabularNums?"tabular-nums":""}},A(v,d=>d&&n("span",{class:`${t}-statistic-value__prefix`},d)),this.value!==void 0?n("span",{class:`${t}-statistic-value__content`},this.value):A(c,d=>d&&n("span",{class:`${t}-statistic-value__content`},d)),A(h,d=>d&&n("span",{class:`${t}-statistic-value__suffix`},d))))}});const G=e=>(ze("data-v-9a07fa30"),e=e(),Te(),e),Ae=["src"],Ve={style:{"margin-bottom":"18px"}},Le={style:{"margin-bottom":"0"}},Ye={key:0},Me={style:{"margin-bottom":"30px"}},We=G(()=>C("h2",null,"\u901A\u8FC7\u7684\u9898\u76EE",-1)),De=G(()=>C("h2",null,"\u6700\u8FD1\u7684\u63D0\u4EA4",-1)),Ue={__name:"_id",setup(e){const t=ge(),c=N(t.params.id),r=N({}),v=()=>{me.get(`/user/${c.value}/`).then(h=>{r.value=h})};return v(),(h,d)=>{const b=Fe,f=ye,S=fe("router-link"),z=Ce,T=je,w=Re,I=Se,k=$e,R=ve;return j(),M(R,{"has-sider":""},{default:u(()=>[g(T,{"content-style":"padding: 24px; text-align: center"},{default:u(()=>[g(z,{vertical:""},{default:u(()=>[C("img",{style:{width:"70%",margin:"auto",display:"block","border-radius":"50%"},src:r.value.avatar||"https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png"},null,8,Ae),C("div",Ve,[C("h1",Le,x(r.value.username),1),r.value.real_name?(j(),U("p",Ye,x(r.value.real_name),1)):H("",!0)]),g(b,{label:"\u901A\u8FC7\u9898\u76EE\u6570"},{default:u(()=>[y(x(r.value.solved_problems&&r.value.solved_problems.length),1)]),_:1}),g(b,{label:"\u901A\u8FC7 / \u63D0\u4EA4\u6B21\u6570"},{prefix:u(()=>[y(x(r.value.accepted_count),1)]),suffix:u(()=>[y(x(r.value.submission_count),1)]),default:u(()=>[y(" / ")]),_:1}),K(he).state.user.permissions.includes("user")?(j(),M(S,{key:0,to:{name:"user_edit",params:{id:c.value}}},{default:u(()=>[g(f,{type:"primary",style:{"margin-top":"10px"}},{default:u(()=>[y("\u7BA1\u7406")]),_:1})]),_:1},8,["to"])):H("",!0)]),_:1})]),_:1}),g(k,{"content-style":"padding: 24px 35px;"},{default:u(()=>[C("div",Me,[We,g(z,{size:"small"},{default:u(()=>[(j(!0),U(xe,null,_e(r.value.solved_problems,p=>(j(),M(I,{trigger:"hover",key:p.problem.id},{trigger:u(()=>[g(S,{to:{name:"problem_detail",params:{id:p.problem.id}}},{default:u(()=>[g(f,{color:K(we)[p.problem.difficulty]},{default:u(()=>[y(" #"+x(p.problem.id)+" | "+x(p.problem.title),1)]),_:2},1032,["color"])]),_:2},1032,["to"])]),default:u(()=>[y(" \u901A\u8FC7\u65F6\u95F4\uFF1A"),g(w,{time:Number(new Date(p.create_time))},null,8,["time"])]),_:2},1024))),128))]),_:1})]),C("div",null,[De,g(ke,{data:r.value.submissions,onRefresh:v},null,8,["data"])])]),_:1})]),_:1})}}},dt=pe(Ue,[["__scopeId","data-v-9a07fa30"]]);export{dt as default};
