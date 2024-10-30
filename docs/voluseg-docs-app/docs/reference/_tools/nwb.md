---
sidebar_label: nwb
title: _tools.nwb
---

## pynwb

## contextmanager

#### open\_nwbfile\_local

```python
@contextmanager
def open_nwbfile_local(file_path: str)
```

Context manager to open and close a local NWB file.

**Arguments**

* **file_path** (`str`): Path to NWB file.

**Yields**

* `pynwb.NWBFile`: The opened NWB file.

#### open\_nwbfile\_remote

```python
@contextmanager
def open_nwbfile_remote(s3_url: str, output_path: str)
```

Context manager to open and close a remote NWB file.

**Arguments**

* **s3_url** (`str`): S3 URL to NWB file.
* **output_path** (`str`): Output path to cache the remote file.

**Yields**

* `pynwb.NWBFile`: The opened NWB file.

#### open\_nwbfile

```python
@contextmanager
def open_nwbfile(input_path: str, remote: bool, output_path: str = None)
```

Open and close an NWB file from either a local or remote source.

**Arguments**

* **input_path** (`str`): Path to the NWB file. This can be a local file path or an S3 URL.
* **remote** (`bool`): If True, the file is assumed to be remote (S3 URL), otherwise, it is assumed to be a local file.
* **output_path** (`str`): Output path, only used to cache remote files.

**Yields**

* `pynwb.NWBFile`: The opened NWB file.

#### find\_nwbfile\_volume\_object\_name

```python
def find_nwbfile_volume_object_name(nwbfile: pynwb.NWBFile) -> str
```

Find the name of the `TwoPhotonSeries` volume object in the NWB file.

**Arguments**

* **nwbfile** (`pynwb.NWBFile`): NWB file.

**Returns**

* `str`: Name of the volume object.

#### get\_nwbfile\_volume

```python
def get_nwbfile_volume(
        nwbfile: pynwb.NWBFile,
        acquisition_name: str = "TwoPhotonSeries") -> pynwb.NWBFile
```

Get `TwoPhotonSeries` object from NWB file.

**Arguments**

* **nwbfile** (`pynwb.NWBFile`): NWB file.
* **acquisition_name** (`str (default: "TwoPhotonSeries")`): Acquisition name.

**Returns**

* `pynwb.NWBFile`: NWB file.

