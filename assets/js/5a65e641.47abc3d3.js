"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[1890],{8943:(e,n,t)=>{t.r(n),t.d(n,{assets:()=>l,contentTitle:()=>s,default:()=>c,frontMatter:()=>r,metadata:()=>a,toc:()=>d});var i=t(4848),o=t(8453);const r={title:"Running on DANDI Hub",sidebar_position:4},s=void 0,a={id:"getting_started/running_dandihub",title:"Running on DANDI Hub",description:"DANDI Hub",source:"@site/docs/getting_started/running_dandihub.mdx",sourceDirName:"getting_started",slug:"/getting_started/running_dandihub",permalink:"/voluseg/docs/getting_started/running_dandihub",draft:!1,unlisted:!1,tags:[],version:"current",sidebarPosition:4,frontMatter:{title:"Running on DANDI Hub",sidebar_position:4},sidebar:"docsSidebar",previous:{title:"Running from Container",permalink:"/voluseg/docs/getting_started/running_container"},next:{title:"Running on AWS Batch",permalink:"/voluseg/docs/getting_started/iac_aws_batch"}},l={},d=[{value:"DANDI Hub",id:"dandi-hub",level:2},{value:"Setup",id:"setup",level:2},{value:"Running Voluseg with Apptainer",id:"running-voluseg-with-apptainer",level:2}];function u(e){const n={a:"a",code:"code",h2:"h2",li:"li",ol:"ol",p:"p",pre:"pre",ul:"ul",...(0,o.R)(),...e.components};return(0,i.jsxs)(i.Fragment,{children:[(0,i.jsx)(n.h2,{id:"dandi-hub",children:"DANDI Hub"}),"\n",(0,i.jsxs)(n.p,{children:["Neuroscientists registered at ",(0,i.jsx)(n.a,{href:"https://dandiarchive.org/",children:"DANDI archive"})," can use the ",(0,i.jsx)(n.a,{href:"https://www.dandiarchive.org/handbook/50_hub/",children:"DANDI Hub"})," to interact with the data stored in the archive.\nDANDI Hub is a JupyterHub instance in the cloud, free to use for exploratory analysis of data on DANDI."]}),"\n",(0,i.jsx)(n.h2,{id:"setup",children:"Setup"}),"\n",(0,i.jsxs)(n.p,{children:["Follow the instructions in the ",(0,i.jsx)(n.a,{href:"https://www.dandiarchive.org/handbook/50_hub/",children:"DANDI Hub Handbook"})," to spin up a Jupyter notebook instance on DANDI Hub."]}),"\n",(0,i.jsx)(n.p,{children:"Once you have a Jupyter notebook running on DANDI Hub, follow these steps:"}),"\n",(0,i.jsxs)(n.ol,{children:["\n",(0,i.jsx)(n.li,{children:"Open a new terminal"}),"\n",(0,i.jsxs)(n.li,{children:["Create a folder for your Voluseg run: ",(0,i.jsx)(n.code,{children:"mkdir my_voluseg_run"})]}),"\n",(0,i.jsxs)(n.li,{children:["Change to the new directory: ",(0,i.jsx)(n.code,{children:"cd my_voluseg_run"})]}),"\n"]}),"\n",(0,i.jsx)(n.h2,{id:"running-voluseg-with-apptainer",children:"Running Voluseg with Apptainer"}),"\n",(0,i.jsx)(n.p,{children:"Pull the image from GHCR and convert it to an Apptainer image:"}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-bash",children:"apptainer pull docker://ghcr.io/mikarubi/voluseg/voluseg:latest\n"})}),"\n",(0,i.jsxs)(n.p,{children:["You should see a ",(0,i.jsx)(n.code,{children:".sif"})," file in your working directory, this is the Voluseg image converted to the Apptainer format."]}),"\n",(0,i.jsx)(n.p,{children:"You can now run the Voluseg pipeline using this Apptainer image. For example:"}),"\n",(0,i.jsx)(n.pre,{children:(0,i.jsx)(n.code,{className:"language-bash",children:'apptainer exec \\\n--bind $(pwd)/output:/voluseg/output  \\\nvoluseg_latest.sif \\\npython3 /voluseg/app/app.py \\\n--registration high \\\n--diam-cell 5.0 \\\n--no-parallel-volume \\\n--no-parallel-clean \\\n--dir-input "https://dandiarchive.s3.amazonaws.com/blobs/057/ecb/057ecbef-e732-4e94-8d99-40ebb74d346e" \\\n2>&1 | tee log_file.log\n'})}),"\n",(0,i.jsx)(n.p,{children:"The command above will:"}),"\n",(0,i.jsxs)(n.ul,{children:["\n",(0,i.jsx)(n.li,{children:"Use the data stored in the S3 path (from DANDI archive) as input"}),"\n",(0,i.jsx)(n.li,{children:"Run the Voluseg pipeline with the user-specified parameters"}),"\n",(0,i.jsxs)(n.li,{children:["Store the output in the ",(0,i.jsx)(n.code,{children:"output"})," directory"]}),"\n",(0,i.jsxs)(n.li,{children:["Save the log output to a file named ",(0,i.jsx)(n.code,{children:"log_file.log"})]}),"\n"]})]})}function c(e={}){const{wrapper:n}={...(0,o.R)(),...e.components};return n?(0,i.jsx)(n,{...e,children:(0,i.jsx)(u,{...e})}):u(e)}},8453:(e,n,t)=>{t.d(n,{R:()=>s,x:()=>a});var i=t(6540);const o={},r=i.createContext(o);function s(e){const n=i.useContext(r);return i.useMemo((function(){return"function"==typeof e?e(n):{...n,...e}}),[n,e])}function a(e){let n;return n=e.disableParentContext?"function"==typeof e.components?e.components(o):e.components||o:s(e.components),i.createElement(r.Provider,{value:n},e.children)}}}]);