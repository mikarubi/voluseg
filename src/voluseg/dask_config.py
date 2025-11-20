"""
Dask configuration utilities for voluseg pipeline.

This script provides comprehensive Dask configuration management,
including the DaskConfig class and all utility functions.
"""

import yaml
from typing import Optional, Dict, Any, Union
from pathlib import Path
import dask
from dask.distributed import Client, LocalCluster
from dask_jobqueue import SLURMCluster, PBSCluster, SGECluster
import logging

logger = logging.getLogger(__name__)


class DaskConfig:
    """
    Comprehensive Dask configuration management class.
    
    Supports both local and cluster configurations with flexible parameter control.
    Includes all utility functions for Dask configuration.
    """
    
    def __init__(
        self,
        n_workers: Optional[int] = None,
        n_cores_per_worker: int = 1,
        memory_limit: Optional[str] = None,
        threads_per_worker: Optional[int] = None,
        cluster_type: str = "local",
        cluster_config: Optional[Dict[str, Any]] = None,
        dashboard_address: Optional[str] = None,
        dashboard_port: Optional[int] = None,
        config_file: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize Dask configuration.
        
        Parameters
        ----------
        n_workers : Optional[int]
            Number of workers. If None, uses all available cores.
        n_cores_per_worker : int
            Number of cores per worker (default: 1).
        memory_limit : Optional[str]
            Memory limit per worker (e.g., "2GB", "4GB").
        threads_per_worker : Optional[int]
            Number of threads per worker. If None, uses n_cores_per_worker.
        cluster_type : str
            Type of cluster: "local", "slurm", "pbs", "sge".
        cluster_config : Optional[Dict[str, Any]]
            Additional cluster-specific configuration.
        dashboard_address : Optional[str]
            Dashboard address for monitoring.
        dashboard_port : Optional[int]
            Dashboard port for monitoring.
        config_file : Optional[Union[str, Path]]
            Path to YAML configuration file.
        """
        self.n_workers = n_workers
        self.n_cores_per_worker = n_cores_per_worker
        self.memory_limit = memory_limit
        self.threads_per_worker = threads_per_worker or n_cores_per_worker
        self.cluster_type = cluster_type
        self.cluster_config = cluster_config or {}
        self.dashboard_address = dashboard_address
        self.dashboard_port = dashboard_port
        self.config_file = config_file
        
        # Load configuration from file if provided
        if config_file:
            self.load_from_file(config_file)
        
        # Set default values
        if self.n_workers is None:
            import multiprocessing
            self.n_workers = multiprocessing.cpu_count()
        
        if self.memory_limit is None:
            self.memory_limit = "2GB"
        
        if self.dashboard_port is None:
            self.dashboard_port = 8787    
    def load_from_file(self, config_file: Union[str, Path]) -> None:
        """
        Load configuration from YAML file.
        
        Parameters
        ----------
        config_file : Union[str, Path]
            Path to YAML configuration file.
        """
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Update instance attributes with loaded config
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def save_to_file(self, config_file: Union[str, Path]) -> None:
        """
        Save current configuration to YAML file.
        
        Parameters
        ----------
        config_file : Union[str, Path]
            Path to save configuration file.
        """
        config = {
            'n_workers': self.n_workers,
            'n_cores_per_worker': self.n_cores_per_worker,
            'memory_limit': self.memory_limit,
            'threads_per_worker': self.threads_per_worker,
            'cluster_type': self.cluster_type,
            'cluster_config': self.cluster_config,
            'dashboard_address': self.dashboard_address,
            'dashboard_port': self.dashboard_port,
        }
        
        config_path = Path(config_file)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
    
    def create_cluster(self):
        """
        Create and return a Dask cluster based on configuration.
        
        Returns
        -------
        cluster
            Dask cluster instance.
        """
        if self.cluster_type == "local":
            return self._create_local_cluster()
        elif self.cluster_type == "slurm":
            return self._create_slurm_cluster()
        elif self.cluster_type == "pbs":
            return self._create_pbs_cluster()
        elif self.cluster_type == "sge":
            return self._create_sge_cluster()
        else:
            raise ValueError(f"Unsupported cluster type: {self.cluster_type}")
    
    def _create_local_cluster(self):
        """Create a local cluster."""
        cluster_config = self.cluster_config.copy()
        dashboard_bind = self._build_dashboard_bind()
        
        cluster = LocalCluster(
            n_workers=self.n_workers,
            threads_per_worker=self.threads_per_worker,
            memory_limit=self.memory_limit,
            dashboard_address=dashboard_bind,
            **cluster_config
        )
        return cluster
    
    def _create_slurm_cluster(self):
        """Create a SLURM cluster."""
        cluster = SLURMCluster(
            cores=self.n_cores_per_worker,
            memory=self.memory_limit,
            **self.cluster_config
        )
        cluster.scale(jobs=self.n_workers)
        return cluster
    
    def _create_pbs_cluster(self):
        """Create a PBS cluster."""
        cluster = PBSCluster(
            cores=self.n_cores_per_worker,
            memory=self.memory_limit,
            **self.cluster_config
        )
        cluster.scale(jobs=self.n_workers)
        return cluster
    
    def _create_sge_cluster(self):
        """Create an SGE cluster."""
        cluster = SGECluster(
            cores=self.n_cores_per_worker,
            memory=self.memory_limit,
            **self.cluster_config
        )
        cluster.scale(jobs=self.n_workers)
        return cluster
    
    def get_client(self, force_new: bool = False) -> Client:
        """
        Get or create a Dask client with the configured cluster.
        
        Parameters
        ----------
        force_new : bool
            If True, close any existing client and create a new one.
            Default is False (reuse existing client if available).
        
        Returns
        -------
        Client
            Dask distributed client.
        """
        if force_new:
            try:
                existing_client = Client.current()
                existing_client.close()
                if hasattr(existing_client, 'cluster') and existing_client.cluster:
                    existing_client.cluster.close()
                logger.info("Closed existing Dask client to create new one")
            except ValueError:
                pass
        
        try:
            # Try to get existing client
            client = Client.current()
            if not force_new:
                logger.info(f"Using existing Dask client: {client}")
                return client
        except ValueError:
            pass
        
        # Create new client
        cluster = self.create_cluster()
        client = Client(cluster)
        logger.info(f"Created new Dask client: {client}")
        return client
    
    def configure_dask(self, force_new: bool = True) -> Client:
        """
        Configure Dask with the current settings and return a client.
        
        Parameters
        ----------
        force_new : bool
            If True, close any existing client and create a new one with
            the new configuration. Default is True to ensure correct configuration.
        
        Returns
        -------
        Client
            Configured Dask client.
        """
        # Set Dask configuration
        # Lower memory thresholds to be more conservative and prevent worker kills
        dask.config.set({
            'distributed.worker.memory.target': 0.6,  # Start spilling earlier
            'distributed.worker.memory.spill': 0.75,   # Spill to disk at 75%
            'distributed.worker.memory.pause': 0.85,   # Pause tasks at 85%
            'distributed.worker.memory.terminate': 0.95, # Terminate at 95%
            # Limit concurrent tasks to reduce memory pressure
            'distributed.worker.tasks.max': 2,  # Max 2 tasks per worker
        })
        
        client = self.get_client(force_new=force_new)
        
        # Log configuration
        logger.info(f"Dask configuration:")
        logger.info(f"  Cluster type: {self.cluster_type}")
        logger.info(f"  Workers: {self.n_workers}")
        logger.info(f"  Cores per worker: {self.n_cores_per_worker}")
        logger.info(f"  Memory limit: {self.memory_limit}")
        logger.info(f"  Dashboard: {client.dashboard_link}")
        
        return client
    
    def _build_dashboard_bind(self):
        """Build dashboard bind address."""
        if self.dashboard_address:
            return self.dashboard_address
        else:
            if self.dashboard_port:
                return f"localhost:{self.dashboard_port}"
            else:
                return None
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        Get current configuration information.
        
        Returns
        -------
        Dict[str, Any]
            Configuration information.
        """
        try:
            client = Client.current()
            cluster = client.cluster
            return {
                'cluster_type': self.cluster_type,
                'n_workers': self.n_workers,
                'n_cores_per_worker': self.n_cores_per_worker,
                'memory_limit': self.memory_limit,
                'threads_per_worker': self.threads_per_worker,
                'dashboard_link': client.dashboard_link,
                'cluster_info': str(cluster),
                'worker_info': str(client.scheduler_info()['workers']),
            }
        except ValueError:
            return {
                'cluster_type': self.cluster_type,
                'n_workers': self.n_workers,
                'n_cores_per_worker': self.n_cores_per_worker,
                'memory_limit': self.memory_limit,
                'threads_per_worker': self.threads_per_worker,
                'status': 'No active client',
            }
    
    def print_info(self):
        """Print current Dask configuration information."""
        try:
            client = Client.current()
            print(f"Dask Dashboard: {client.dashboard_link}")
            print(f"Cluster: {client.cluster}")
            print(f"Workers: {len(client.scheduler_info()['workers'])}")
        except ValueError:
            print("No active Dask client found.")
    
    @staticmethod
    def configure_from_parameters(parameters: dict) -> Client:
        """
        Configure Dask from voluseg parameters.
        
        Parameters
        ----------
        parameters : dict
            voluseg parameters dictionary.
        
        Returns
        -------
        Client
            Configured Dask client.
        """
        # Extract Dask configuration from parameters
        dask_config = parameters.get('dask_config', {})
        
        # Create DaskConfig instance
        config = DaskConfig(
            n_workers=dask_config.get('n_workers'),
            n_cores_per_worker=dask_config.get('n_cores_per_worker', 1),
            memory_limit=dask_config.get('memory_limit'),
            threads_per_worker=dask_config.get('threads_per_worker'),
            cluster_type=dask_config.get('cluster_type', 'local'),
            cluster_config=dask_config.get('cluster_config', {}),
            dashboard_address=dask_config.get('dashboard_address'),
            dashboard_port=dask_config.get('dashboard_port'),
            config_file=dask_config.get('config_file'),
        )
        
        return config.configure_dask()
    
    @staticmethod
    def get_current_client() -> Client:
        """
        Get the current Dask client or create a default one.
        
        Returns
        -------
        Client
            Dask client.
        """
        try:
            return Client.current()
        except ValueError:
            # Create default client
            config = DaskConfig()
            return config.configure_dask()
    
    @staticmethod
    def print_current_info():
        """Print current Dask configuration information."""
        try:
            client = Client.current()
            print(f"Dask Dashboard: {client.dashboard_link}")
            print(f"Cluster: {client.cluster}")
            print(f"Workers: {len(client.scheduler_info()['workers'])}")
        except ValueError:
            print("No active Dask client found.")


# Convenience functions for backward compatibility
def configure_dask_from_parameters(parameters: dict) -> Client:
    """Configure Dask from voluseg parameters."""
    return DaskConfig.configure_from_parameters(parameters)


def get_dask_client() -> Client:
    """Get the current Dask client or create a default one."""
    return DaskConfig.get_current_client()


def print_dask_info():
    """Print current Dask configuration information."""
    DaskConfig.print_current_info()
