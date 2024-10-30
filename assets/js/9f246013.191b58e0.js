"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[510],{498:(e,n,i)=>{i.r(n),i.d(n,{assets:()=>a,contentTitle:()=>o,default:()=>h,frontMatter:()=>r,metadata:()=>l,toc:()=>d});var t=i(4848),s=i(8453);const r={sidebar_label:"parameter_dictionary",title:"tools.parameter_dictionary"},o=void 0,l={id:"reference/tools/parameter_dictionary",title:"tools.parameter_dictionary",description:"Union",source:"@site/docs/reference/tools/parameter_dictionary.md",sourceDirName:"reference/tools",slug:"/reference/tools/parameter_dictionary",permalink:"/voluseg/docs/reference/tools/parameter_dictionary",draft:!1,unlisted:!1,tags:[],version:"current",frontMatter:{sidebar_label:"parameter_dictionary",title:"tools.parameter_dictionary"},sidebar:"docsSidebar",previous:{title:"nwb",permalink:"/voluseg/docs/reference/tools/nwb"},next:{title:"parameters",permalink:"/voluseg/docs/reference/tools/parameters"}},a={},d=[{value:"Union",id:"union",level:2},{value:"ParametersModel",id:"parametersmodel",level:2},{value:"parameter_dictionary",id:"parameter_dictionary",level:4}];function c(e){const n={code:"code",h2:"h2",h4:"h4",li:"li",p:"p",pre:"pre",strong:"strong",ul:"ul",...(0,s.R)(),...e.components};return(0,t.jsxs)(t.Fragment,{children:[(0,t.jsx)(n.h2,{id:"union",children:"Union"}),"\n",(0,t.jsx)(n.h2,{id:"parametersmodel",children:"ParametersModel"}),"\n",(0,t.jsx)(n.h4,{id:"parameter_dictionary",children:"parameter_dictionary"}),"\n",(0,t.jsx)(n.pre,{children:(0,t.jsx)(n.code,{className:"language-python",children:'def parameter_dictionary(detrending: str = "standard",\n                         registration: str = "medium",\n                         registration_restrict: str = "",\n                         diam_cell: float = 6.0,\n                         dir_ants: str = "",\n                         dir_input: str = "",\n                         dir_output: str = "",\n                         dir_transform: str = "",\n                         ds: int = 2,\n                         planes_pad: int = 0,\n                         planes_packed: bool = False,\n                         parallel_clean: bool = True,\n                         parallel_volume: bool = True,\n                         save_volume: bool = False,\n                         type_timepoints: str = "dff",\n                         type_mask: str = "geomean",\n                         timepoints: int = 1000,\n                         f_hipass: float = 0,\n                         f_volume: float = 2.0,\n                         n_cells_block: int = 316,\n                         n_colors: int = 1,\n                         res_x: float = 0.40625,\n                         res_y: float = 0.40625,\n                         res_z: float = 5.0,\n                         t_baseline: int = 300,\n                         t_section: float = 0.01,\n                         thr_mask: float = 0.5,\n                         volume_fullnames_input: Union[list[str], None] = None,\n                         volume_names: Union[list[str], None] = None,\n                         input_dirs: Union[list[str], None] = None,\n                         ext: Union[str, None] = None,\n                         lt: Union[int, None] = None,\n                         affine_matrix: Union[list, None] = None) -> dict\n'})}),"\n",(0,t.jsx)(n.p,{children:"Return a parameter dictionary with specified defaults."}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Arguments"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"detrending"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Type of detrending: 'standard', 'robust', or 'none' (default is 'standard')."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"registration"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Quality of registration: 'high', 'medium', 'low' or 'none' (default is 'medium')."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"registration_restrict"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Restrict registration (e.g. 1x1x1x1x1x1x0x0x0x1x1x0) (default is an empty string)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"diam_cell"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): Cell diameter in microns (default is 6.0)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"dir_ants"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Path to the ANTs directory (default is an empty string)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"dir_input"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Path to input directories, separate multiple directories with ';' (default is an empty string)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"dir_output"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Path to the output directory (default is an empty string)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"dir_transform"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Path to the transform directory (default is an empty string)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"ds"})," (",(0,t.jsx)(n.code,{children:"int, optional"}),"): Spatial coarse-graining in x-y dimension (default is 2)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"planes_pad"})," (",(0,t.jsx)(n.code,{children:"int, optional"}),"): Number of planes to pad the volume with for robust registration (default is 0)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"planes_packed"})," (",(0,t.jsx)(n.code,{children:"bool, optional"}),"): Packed planes in each volume, for single plane imaging with packed planes (default is False)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"parallel_clean"})," (",(0,t.jsx)(n.code,{children:"bool, optional"}),"): Parallelization of final cleaning (True is fast but memory-intensive, default is True)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"parallel_volume"})," (",(0,t.jsx)(n.code,{children:"bool, optional"}),"): Parallelization of mean-volume computation (True is fast but memory-intensive, default is True)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"save_volume"})," (",(0,t.jsx)(n.code,{children:"bool, optional"}),"): Save registered volumes after segmentation, True keeps a copy of the volumes (default is False)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"type_timepoints"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Type of timepoints to use for cell detection: 'dff', 'periodic' or 'custom' (default is 'dff')."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"type_mask"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): Type of volume averaging for the mask: 'mean', 'geomean' or 'max' (default is 'geomean')."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"timepoints"})," (",(0,t.jsx)(n.code,{children:"int, optional"}),"): Number ('dff', 'periodic') or vector ('custom') of timepoints for segmentation (default is 1000)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"f_hipass"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): Frequency (Hz) for high-pass filtering of cell timeseries (default is 0)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"f_volume"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): Imaging frequency in Hz (default is 2.0)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"n_cells_block"})," (",(0,t.jsx)(n.code,{children:"int, optional"}),"): Number of cells in a block. Small number is fast but can lead to blocky output (default is 316)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"n_colors"})," (",(0,t.jsx)(n.code,{children:"int, optional"}),"): Number of brain colors (2 in two-color volumes, default is 1)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"res_x"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): X resolution in microns (default is 0.40625)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"res_y"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): Y resolution in microns (default is 0.40625)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"res_z"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): Z resolution in microns (default is 5.0)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"t_baseline"})," (",(0,t.jsx)(n.code,{children:"int, optional"}),"): Interval for baseline calculation in seconds (default is 300)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"t_section"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): Exposure time in seconds for slice acquisition (default is 0.01)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"thr_mask"})," (",(0,t.jsx)(n.code,{children:"float, optional"}),"): Threshold for volume mask: 0 < thr <= 1 (probability) or thr > 1 (intensity) (default is 0.5)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"volume_fullnames_input"})," (",(0,t.jsx)(n.code,{children:"list[str], optional"}),"): List of full volume names (default is None)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"volume_names"})," (",(0,t.jsx)(n.code,{children:"list[str], optional"}),"): List of volume names (default is None)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"input_dirs"})," (",(0,t.jsx)(n.code,{children:"list[str], optional"}),"): List of input directories (default is None)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"ext"})," (",(0,t.jsx)(n.code,{children:"str, optional"}),"): File extension (default is None)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"lt"})," (",(0,t.jsx)(n.code,{children:"int, optional"}),"): Number of volumes (default is None)."]}),"\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.strong,{children:"affine_matrix"})," (",(0,t.jsx)(n.code,{children:"list, optional"}),"): Affine matrix (default is None)."]}),"\n"]}),"\n",(0,t.jsx)(n.p,{children:(0,t.jsx)(n.strong,{children:"Returns"})}),"\n",(0,t.jsxs)(n.ul,{children:["\n",(0,t.jsxs)(n.li,{children:[(0,t.jsx)(n.code,{children:"dict"}),": A dictionary of validated parameters with their default values."]}),"\n"]})]})}function h(e={}){const{wrapper:n}={...(0,s.R)(),...e.components};return n?(0,t.jsx)(n,{...e,children:(0,t.jsx)(c,{...e})}):c(e)}},8453:(e,n,i)=>{i.d(n,{R:()=>o,x:()=>l});var t=i(6540);const s={},r=t.createContext(s);function o(e){const n=t.useContext(r);return t.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function l(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(s):e.components||s:o(e.components),t.createElement(r.Provider,{value:n},e.children)}}}]);