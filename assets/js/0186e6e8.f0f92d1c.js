"use strict";(self.webpackChunkdocs=self.webpackChunkdocs||[]).push([[7074],{596:e=>{e.exports=JSON.parse('{"version":{"pluginId":"default","version":"current","label":"Next","banner":null,"badge":false,"noIndex":false,"className":"docs-version-current","isLast":true,"docsSidebars":{"docsSidebar":[{"type":"link","label":"Introduction","href":"/voluseg/docs/intro","docId":"intro","unlisted":false},{"type":"category","label":"Getting Started","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"Installation","href":"/voluseg/docs/getting_started/installation","docId":"getting_started/installation","unlisted":false},{"type":"link","label":"Running Voluseg Pipeline","href":"/voluseg/docs/getting_started/running","docId":"getting_started/running","unlisted":false},{"type":"link","label":"Running from Container","href":"/voluseg/docs/getting_started/running_container","docId":"getting_started/running_container","unlisted":false},{"type":"link","label":"Running on DANDI Hub","href":"/voluseg/docs/getting_started/running_dandihub","docId":"getting_started/running_dandihub","unlisted":false},{"type":"link","label":"Running on AWS Batch","href":"/voluseg/docs/getting_started/iac_aws_batch","docId":"getting_started/iac_aws_batch","unlisted":false},{"type":"link","label":"Pipeline Parameters","href":"/voluseg/docs/getting_started/parameters","docId":"getting_started/parameters","unlisted":false}],"href":"/voluseg/docs/category/getting-started"},{"type":"category","label":"API Reference","collapsible":true,"collapsed":true,"items":[{"type":"category","label":"steps","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"step0","href":"/voluseg/docs/reference/steps/step0","docId":"reference/steps/step0","unlisted":false},{"type":"link","label":"step1","href":"/voluseg/docs/reference/steps/step1","docId":"reference/steps/step1","unlisted":false},{"type":"link","label":"step2","href":"/voluseg/docs/reference/steps/step2","docId":"reference/steps/step2","unlisted":false},{"type":"link","label":"step3","href":"/voluseg/docs/reference/steps/step3","docId":"reference/steps/step3","unlisted":false},{"type":"link","label":"step4","href":"/voluseg/docs/reference/steps/step4","docId":"reference/steps/step4","unlisted":false},{"type":"link","label":"step4a","href":"/voluseg/docs/reference/steps/step4a","docId":"reference/steps/step4a","unlisted":false},{"type":"link","label":"step4b","href":"/voluseg/docs/reference/steps/step4b","docId":"reference/steps/step4b","unlisted":false},{"type":"link","label":"step4c","href":"/voluseg/docs/reference/steps/step4c","docId":"reference/steps/step4c","unlisted":false},{"type":"link","label":"step4d","href":"/voluseg/docs/reference/steps/step4d","docId":"reference/steps/step4d","unlisted":false},{"type":"link","label":"step4e","href":"/voluseg/docs/reference/steps/step4e","docId":"reference/steps/step4e","unlisted":false},{"type":"link","label":"step5","href":"/voluseg/docs/reference/steps/step5","docId":"reference/steps/step5","unlisted":false}]},{"type":"category","label":"tools","collapsible":true,"collapsed":true,"items":[{"type":"link","label":"ants_registration","href":"/voluseg/docs/reference/tools/ants_registration","docId":"reference/tools/ants_registration","unlisted":false},{"type":"link","label":"ants_transformation","href":"/voluseg/docs/reference/tools/ants_transformation","docId":"reference/tools/ants_transformation","unlisted":false},{"type":"link","label":"aws","href":"/voluseg/docs/reference/tools/aws","docId":"reference/tools/aws","unlisted":false},{"type":"link","label":"ball","href":"/voluseg/docs/reference/tools/ball","docId":"reference/tools/ball","unlisted":false},{"type":"link","label":"clean_signal","href":"/voluseg/docs/reference/tools/clean_signal","docId":"reference/tools/clean_signal","unlisted":false},{"type":"link","label":"constants","href":"/voluseg/docs/reference/tools/constants","docId":"reference/tools/constants","unlisted":false},{"type":"link","label":"evenly_parallelize","href":"/voluseg/docs/reference/tools/evenly_parallelize","docId":"reference/tools/evenly_parallelize","unlisted":false},{"type":"link","label":"get_volume_name","href":"/voluseg/docs/reference/tools/get_volume_name","docId":"reference/tools/get_volume_name","unlisted":false},{"type":"link","label":"load_metadata","href":"/voluseg/docs/reference/tools/load_metadata","docId":"reference/tools/load_metadata","unlisted":false},{"type":"link","label":"load_volume","href":"/voluseg/docs/reference/tools/load_volume","docId":"reference/tools/load_volume","unlisted":false},{"type":"link","label":"nwb","href":"/voluseg/docs/reference/tools/nwb","docId":"reference/tools/nwb","unlisted":false},{"type":"link","label":"parameter_dictionary","href":"/voluseg/docs/reference/tools/parameter_dictionary","docId":"reference/tools/parameter_dictionary","unlisted":false},{"type":"link","label":"parameters","href":"/voluseg/docs/reference/tools/parameters","docId":"reference/tools/parameters","unlisted":false},{"type":"link","label":"parameters_models","href":"/voluseg/docs/reference/tools/parameters_models","docId":"reference/tools/parameters_models","unlisted":false},{"type":"link","label":"sample_data","href":"/voluseg/docs/reference/tools/sample_data","docId":"reference/tools/sample_data","unlisted":false},{"type":"link","label":"save_volume","href":"/voluseg/docs/reference/tools/save_volume","docId":"reference/tools/save_volume","unlisted":false},{"type":"link","label":"sparseness","href":"/voluseg/docs/reference/tools/sparseness","docId":"reference/tools/sparseness","unlisted":false},{"type":"link","label":"sparseness_projection","href":"/voluseg/docs/reference/tools/sparseness_projection","docId":"reference/tools/sparseness_projection","unlisted":false}]},{"type":"link","label":"update","href":"/voluseg/docs/reference/update","docId":"reference/update","unlisted":false}],"href":"/voluseg/docs/category/api-reference"},{"type":"link","label":"FAQ","href":"/voluseg/docs/faq","docId":"faq","unlisted":false}]},"docs":{"faq":{"id":"faq","title":"FAQ","description":"Frequently Asked Questions","sidebar":"docsSidebar"},"getting_started/iac_aws_batch":{"id":"getting_started/iac_aws_batch","title":"Running on AWS Batch","description":"Here we provide instructions for setting up your Voluseg service to run jobs in AWS Batch. First you will need to provision the base AWS Batch infrastructure using CDK. This includes IAM roles, VPC, Security Group, Batch Compute Environments and Batch Job Queues. Next you will need to configure your compute resource controller to submit jobs to AWS Batch. Finally, when you submit jobs from the web interface, you must select aws_batch as the run method.","sidebar":"docsSidebar"},"getting_started/installation":{"id":"getting_started/installation","title":"Installation","description":"Prerequisites","sidebar":"docsSidebar"},"getting_started/parameters":{"id":"getting_started/parameters","title":"Pipeline Parameters","description":"Parameters dictionary","sidebar":"docsSidebar"},"getting_started/running":{"id":"getting_started/running","title":"Running Voluseg Pipeline","description":"Pipeline Overview","sidebar":"docsSidebar"},"getting_started/running_container":{"id":"getting_started/running_container","title":"Running from Container","description":"You can easily run the Voluseg pipeline using a container. This is useful if you want to run the pipeline without having to install all the dependencies on your local machine.","sidebar":"docsSidebar"},"getting_started/running_dandihub":{"id":"getting_started/running_dandihub","title":"Running on DANDI Hub","description":"DANDI Hub","sidebar":"docsSidebar"},"intro":{"id":"intro","title":"Introduction","description":"\ud83c\udf1f Welcome to Voluseg, an open-source tool providing a pipeline for automatic volumetric cell segmentation from calcium imaging recordings.","sidebar":"docsSidebar"},"reference/steps/step0":{"id":"reference/steps/step0","title":"steps.step0","description":"process\\\\_parameters","sidebar":"docsSidebar"},"reference/steps/step1":{"id":"reference/steps/step1","title":"steps.step1","description":"process\\\\_volumes","sidebar":"docsSidebar"},"reference/steps/step2":{"id":"reference/steps/step2","title":"steps.step2","description":"align\\\\_volumes","sidebar":"docsSidebar"},"reference/steps/step3":{"id":"reference/steps/step3","title":"steps.step3","description":"mask\\\\_volumes","sidebar":"docsSidebar"},"reference/steps/step4":{"id":"reference/steps/step4","title":"steps.step4","description":"detect\\\\_cells","sidebar":"docsSidebar"},"reference/steps/step4a":{"id":"reference/steps/step4a","title":"steps.step4a","description":"define\\\\_blocks","sidebar":"docsSidebar"},"reference/steps/step4b":{"id":"reference/steps/step4b","title":"steps.step4b","description":"process\\\\block\\\\data","sidebar":"docsSidebar"},"reference/steps/step4c":{"id":"reference/steps/step4c","title":"steps.step4c","description":"initialize\\\\block\\\\cells","sidebar":"docsSidebar"},"reference/steps/step4d":{"id":"reference/steps/step4d","title":"steps.step4d","description":"nnmf\\\\_sparse","sidebar":"docsSidebar"},"reference/steps/step4e":{"id":"reference/steps/step4e","title":"steps.step4e","description":"collect\\\\_blocks","sidebar":"docsSidebar"},"reference/steps/step5":{"id":"reference/steps/step5","title":"steps.step5","description":"clean\\\\_cells","sidebar":"docsSidebar"},"reference/tools/ants_registration":{"id":"reference/tools/ants_registration","title":"tools.ants_registration","description":"ants\\\\_registration","sidebar":"docsSidebar"},"reference/tools/ants_transformation":{"id":"reference/tools/ants_transformation","title":"tools.ants_transformation","description":"ants\\\\_transformation","sidebar":"docsSidebar"},"reference/tools/aws":{"id":"reference/tools/aws","title":"tools.aws","description":"JobDefinitionException Objects","sidebar":"docsSidebar"},"reference/tools/ball":{"id":"reference/tools/ball","title":"tools.ball","description":"ball","sidebar":"docsSidebar"},"reference/tools/clean_signal":{"id":"reference/tools/clean_signal","title":"tools.clean_signal","description":"clean\\\\_signal","sidebar":"docsSidebar"},"reference/tools/constants":{"id":"reference/tools/constants","title":"tools.constants","description":"ori","sidebar":"docsSidebar"},"reference/tools/evenly_parallelize":{"id":"reference/tools/evenly_parallelize","title":"tools.evenly_parallelize","description":"evenly\\\\_parallelize","sidebar":"docsSidebar"},"reference/tools/get_volume_name":{"id":"reference/tools/get_volume_name","title":"tools.get_volume_name","description":"get\\\\volume\\\\name","sidebar":"docsSidebar"},"reference/tools/load_metadata":{"id":"reference/tools/load_metadata","title":"tools.load_metadata","description":"load\\\\_metadata","sidebar":"docsSidebar"},"reference/tools/load_volume":{"id":"reference/tools/load_volume","title":"tools.load_volume","description":"load\\\\_volume","sidebar":"docsSidebar"},"reference/tools/nwb":{"id":"reference/tools/nwb","title":"tools.nwb","description":"open\\\\nwbfile\\\\local","sidebar":"docsSidebar"},"reference/tools/parameter_dictionary":{"id":"reference/tools/parameter_dictionary","title":"tools.parameter_dictionary","description":"parameter\\\\_dictionary","sidebar":"docsSidebar"},"reference/tools/parameters":{"id":"reference/tools/parameters","title":"tools.parameters","description":"load\\\\_parameters","sidebar":"docsSidebar"},"reference/tools/parameters_models":{"id":"reference/tools/parameters_models","title":"tools.parameters_models","description":"Detrending Objects","sidebar":"docsSidebar"},"reference/tools/sample_data":{"id":"reference/tools/sample_data","title":"tools.sample_data","description":"download\\\\sample\\\\data","sidebar":"docsSidebar"},"reference/tools/save_volume":{"id":"reference/tools/save_volume","title":"tools.save_volume","description":"save\\\\_volume","sidebar":"docsSidebar"},"reference/tools/sparseness":{"id":"reference/tools/sparseness","title":"tools.sparseness","description":"sparseness","sidebar":"docsSidebar"},"reference/tools/sparseness_projection":{"id":"reference/tools/sparseness_projection","title":"tools.sparseness_projection","description":"sparseness\\\\_projection","sidebar":"docsSidebar"},"reference/update":{"id":"reference/update","title":"update","description":"voluseg\\\\_update","sidebar":"docsSidebar"}}}}')}}]);