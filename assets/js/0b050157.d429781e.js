"use strict";(self.webpackChunkstarknet_devnet=self.webpackChunkstarknet_devnet||[]).push([[293],{3905:(e,t,n)=>{n.d(t,{Zo:()=>l,kt:()=>m});var r=n(7294);function o(e,t,n){return t in e?Object.defineProperty(e,t,{value:n,enumerable:!0,configurable:!0,writable:!0}):e[t]=n,e}function a(e,t){var n=Object.keys(e);if(Object.getOwnPropertySymbols){var r=Object.getOwnPropertySymbols(e);t&&(r=r.filter((function(t){return Object.getOwnPropertyDescriptor(e,t).enumerable}))),n.push.apply(n,r)}return n}function i(e){for(var t=1;t<arguments.length;t++){var n=null!=arguments[t]?arguments[t]:{};t%2?a(Object(n),!0).forEach((function(t){o(e,t,n[t])})):Object.getOwnPropertyDescriptors?Object.defineProperties(e,Object.getOwnPropertyDescriptors(n)):a(Object(n)).forEach((function(t){Object.defineProperty(e,t,Object.getOwnPropertyDescriptor(n,t))}))}return e}function p(e,t){if(null==e)return{};var n,r,o=function(e,t){if(null==e)return{};var n,r,o={},a=Object.keys(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||(o[n]=e[n]);return o}(e,t);if(Object.getOwnPropertySymbols){var a=Object.getOwnPropertySymbols(e);for(r=0;r<a.length;r++)n=a[r],t.indexOf(n)>=0||Object.prototype.propertyIsEnumerable.call(e,n)&&(o[n]=e[n])}return o}var s=r.createContext({}),c=function(e){var t=r.useContext(s),n=t;return e&&(n="function"==typeof e?e(t):i(i({},t),e)),n},l=function(e){var t=c(e.components);return r.createElement(s.Provider,{value:t},e.children)},u={inlineCode:"code",wrapper:function(e){var t=e.children;return r.createElement(r.Fragment,{},t)}},d=r.forwardRef((function(e,t){var n=e.components,o=e.mdxType,a=e.originalType,s=e.parentName,l=p(e,["components","mdxType","originalType","parentName"]),d=c(n),m=o,b=d["".concat(s,".").concat(m)]||d[m]||u[m]||a;return n?r.createElement(b,i(i({ref:t},l),{},{components:n})):r.createElement(b,i({ref:t},l))}));function m(e,t){var n=arguments,o=t&&t.mdxType;if("string"==typeof e||o){var a=n.length,i=new Array(a);i[0]=d;var p={};for(var s in t)hasOwnProperty.call(t,s)&&(p[s]=t[s]);p.originalType=e,p.mdxType="string"==typeof e?e:o,i[1]=p;for(var c=2;c<a;c++)i[c]=n[c];return r.createElement.apply(null,i)}return r.createElement.apply(null,n)}d.displayName="MDXCreateElement"},375:(e,t,n)=>{n.r(t),n.d(t,{assets:()=>s,contentTitle:()=>i,default:()=>u,frontMatter:()=>a,metadata:()=>p,toc:()=>c});var r=n(7462),o=(n(7294),n(3905));const a={sidebar_position:3},i="JSON-RPC API",p={unversionedId:"guide/json-rpc-api",id:"guide/json-rpc-api",title:"JSON-RPC API",description:"Devnet also supports JSON-RPC API v0.2.0",source:"@site/docs/guide/json-rpc-api.md",sourceDirName:"guide",slug:"/guide/json-rpc-api",permalink:"/starknet-devnet/docs/guide/json-rpc-api",draft:!1,editUrl:"https://github.com/Shard-Labs/starknet-devnet/docs/guide/json-rpc-api.md",tags:[],version:"current",sidebarPosition:3,frontMatter:{sidebar_position:3},sidebar:"tutorialSidebar",previous:{title:"Interaction",permalink:"/starknet-devnet/docs/guide/Interaction"},next:{title:"Dumping & Loading",permalink:"/starknet-devnet/docs/guide/dumping-and-loading"}},s={},c=[],l={toc:c};function u(e){let{components:t,...n}=e;return(0,o.kt)("wrapper",(0,r.Z)({},l,n,{components:t,mdxType:"MDXLayout"}),(0,o.kt)("h1",{id:"json-rpc-api"},"JSON-RPC API"),(0,o.kt)("p",null,"Devnet also supports JSON-RPC API v0.2.0: ",(0,o.kt)("a",{parentName:"p",href:"https://github.com/starkware-libs/starknet-specs/releases/tag/v0.2.0"},"specifications")," . It can be reached under ",(0,o.kt)("inlineCode",{parentName:"p"},"/rpc"),". For an example:"),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre"},'POST /rpc\n{\n  "jsonrpc": "2.0",\n  "method": "starknet_getBlockTransactionCount",\n  "params": {\n    "block_id": "latest"\n  },\n  "id": 0\n}\n')),(0,o.kt)("p",null,"Response:"),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre"},'{\n  "id": 0,\n  "jsonrpc": "2.0",\n  "result": 1\n}\n')),(0,o.kt)("p",null,"Methods that require a ",(0,o.kt)("inlineCode",{parentName:"p"},"block_id")," only support ids of the ",(0,o.kt)("inlineCode",{parentName:"p"},"latest")," or ",(0,o.kt)("inlineCode",{parentName:"p"},"pending")," block.\nPlease note however, that the ",(0,o.kt)("inlineCode",{parentName:"p"},"pending")," block will be the same block as the ",(0,o.kt)("inlineCode",{parentName:"p"},"latest"),"."),(0,o.kt)("pre",null,(0,o.kt)("code",{parentName:"pre",className:"language-js"},'// Use latest\n{\n  "block_id": "latest"\n}\n\n// or pending\n{\n  "block_id": "pending"\n}\n\n// or block number\n{\n  "block_id": {\n    "block_number": 1234  // Must be the number of the latest block\n  }\n}\n\n// or block hash\n{\n  "block_id": {\n    "block_hash": "0x1234" // Must be hash of the latest block\n  }\n}\n')))}u.isMDXComponent=!0}}]);