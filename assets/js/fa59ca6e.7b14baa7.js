"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[3397],{288:(e,n,s)=>{s.r(n),s.d(n,{assets:()=>o,contentTitle:()=>t,default:()=>p,frontMatter:()=>l,metadata:()=>c,toc:()=>d});var r=s(4848),i=s(8453);const l={sidebar_label:"step4c",title:"steps.step4c"},t=void 0,c={id:"reference/steps/step4c",title:"steps.step4c",description:"initialize\\block\\cells",source:"@site/docs/reference/steps/step4c.md",sourceDirName:"reference/steps",slug:"/reference/steps/step4c",permalink:"/voluseg/docs/reference/steps/step4c",draft:!1,unlisted:!1,tags:[],version:"current",frontMatter:{sidebar_label:"step4c",title:"steps.step4c"},sidebar:"docsSidebar",previous:{title:"step4b",permalink:"/voluseg/docs/reference/steps/step4b"},next:{title:"step4d",permalink:"/voluseg/docs/reference/steps/step4d"}},o={},d=[{value:"initialize_block_cells",id:"initialize_block_cells",level:4}];function a(e){const n={code:"code",h4:"h4",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,i.R)(),...e.components};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(n.h4,{id:"initialize_block_cells",children:"initialize_block_cells"}),"\n",(0,r.jsx)(n.pre,{children:(0,r.jsx)(n.code,{className:"language-python",children:"def initialize_block_cells(\n    n_voxels_cell: int, n_voxels_block: int, n_cells: int,\n    voxel_xyz: np.ndarray, voxel_timeseries: np.ndarray, peak_idx: np.ndarray,\n    peak_valids: np.ndarray, voxel_similarity_peak: np.ndarray,\n    lxyz: Tuple[int, int, int], rxyz: Tuple[float, float, float],\n    ball_diam: np.ndarray, ball_diam_xyz0: np.ndarray\n) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]\n"})}),"\n",(0,r.jsx)(n.p,{children:"Initialize cell positions in individual blocks."}),"\n",(0,r.jsx)(n.p,{children:(0,r.jsx)(n.strong,{children:"Arguments"})}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"n_voxels_cell"})," (",(0,r.jsx)(n.code,{children:"int"}),"): Number of voxels in each cell."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"n_voxels_block"})," (",(0,r.jsx)(n.code,{children:"int"}),"): Number of voxels in block."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"n_cells"})," (",(0,r.jsx)(n.code,{children:"int"}),"): Number of cells."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"voxel_xyz"})," (",(0,r.jsx)(n.code,{children:"np.ndarray"}),"): Voxel coordinates."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"voxel_timeseries"})," (",(0,r.jsx)(n.code,{children:"np.ndarray"}),"): Voxel timeseries."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"peak_idx"})," (",(0,r.jsx)(n.code,{children:"np.ndarray"}),"): Peak indices."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"peak_valids"})," (",(0,r.jsx)(n.code,{children:"np.ndarray"}),"): Valid local-intensity maxima (used to determine number of cells)."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"voxel_similarity_peak"})," (",(0,r.jsx)(n.code,{children:"np.ndarray"}),"): Similarity between voxels: defined by the combination of spatial proximity\nand temporal similarity (the voxels are neighbors of each other and also\ncorrelated with each other)."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"lxyz"})," (",(0,r.jsx)(n.code,{children:"Tuple[int, int, int]"}),"): Number of voxels in x, y, and z dimensions."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"rxyz"})," (",(0,r.jsx)(n.code,{children:"Tuple[float, float, float]"}),"): Resolution of x, y, z dimensions."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"ball_diam"})," (",(0,r.jsx)(n.code,{children:"np.ndarray"}),"): Diameter of a sphere that may defines a cell boundary."]}),"\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.strong,{children:"ball_diam_xyz0"})," (",(0,r.jsx)(n.code,{children:"np.ndarray"}),"): Midpoint of the sphere."]}),"\n"]}),"\n",(0,r.jsx)(n.p,{children:(0,r.jsx)(n.strong,{children:"Returns"})}),"\n",(0,r.jsxs)(n.ul,{children:["\n",(0,r.jsxs)(n.li,{children:[(0,r.jsx)(n.code,{children:"Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]"}),": TODO - add description"]}),"\n"]})]})}function p(e={}){const{wrapper:n}={...(0,i.R)(),...e.components};return n?(0,r.jsx)(n,{...e,children:(0,r.jsx)(a,{...e})}):a(e)}},8453:(e,n,s)=>{s.d(n,{R:()=>t,x:()=>c});var r=s(6540);const i={},l=r.createContext(i);function t(e){const n=r.useContext(l);return r.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function c(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(i):e.components||i:t(e.components),r.createElement(l.Provider,{value:n},e.children)}}}]);