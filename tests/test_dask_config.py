"""
Tests for Dask configuration functionality.
"""

import pytest
import tempfile
import os
from pathlib import Path
import yaml
import time

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from voluseg.dask_config import DaskConfig
from voluseg.dask_config import configure_dask_from_parameters, get_dask_client
from dask.distributed import Client


def teardown_function():
    """Clean up Dask clients after each test to prevent memory issues."""
    try:
        # Get current client and close it
        client = Client.current()
        client.close()
        print("✓ Dask client closed successfully")
    except ValueError:
        # No active client, which is fine
        pass
    except Exception as e:
        print(f"Warning: Error closing Dask client: {e}")


def test_dask_setup_success():
    """Test that Dask setup is successful with basic configuration."""
    # Test basic DaskConfig creation and setup
    config = DaskConfig(
        n_workers=2,
        n_cores_per_worker=1,
        memory_limit="1GB",
        cluster_type="local"
    )
    
    # Verify configuration is set correctly
    assert config.n_workers == 2
    assert config.n_cores_per_worker == 1
    assert config.memory_limit == "1GB"
    assert config.cluster_type == "local"
    
    # Test that we can create a client successfully
    client = config.configure_dask()
    assert client is not None
    assert hasattr(client, 'dashboard_link')
    assert hasattr(client, 'cluster')
    
    # Verify the client is actually working
    assert client.dashboard_link is not None
    assert "http://" in client.dashboard_link
    
    # Test that we can get scheduler info (indicates cluster is running)
    scheduler_info = client.scheduler_info()
    assert 'workers' in scheduler_info
    assert len(scheduler_info['workers']) > 0
    
    print(f"✓ Dask setup successful!")
    print(f"  - Dashboard: {client.dashboard_link}")
    print(f"  - Workers: {len(scheduler_info['workers'])}")
    print(f"  - Cluster: {client.cluster}")


def test_dask_setup_from_parameters():
    """Test that Dask setup is successful when configured from voluseg parameters."""
    parameters = {
        'dask_config': {
            'n_workers': 1,
            'n_cores_per_worker': 1,
            'memory_limit': '1GB',
            'cluster_type': 'local'
        }
    }
    
    # Test the utility function
    client = configure_dask_from_parameters(parameters)
    assert client is not None
    assert hasattr(client, 'dashboard_link')
    
    # Verify the setup is working
    scheduler_info = client.scheduler_info()
    assert 'workers' in scheduler_info
    assert len(scheduler_info['workers']) >= 1
    
    # Test that we can actually compute something
    from dask import delayed
    import dask
    
    @delayed
    def simple_task(x):
        return x * 2
    
    # Create a simple computation
    result = simple_task(5)
    computed_result = result.compute()
    assert computed_result == 10
    
    print(f"✓ Dask setup from parameters successful!")
    print(f"  - Dashboard: {client.dashboard_link}")
    print(f"  - Workers: {len(scheduler_info['workers'])}")
    print(f"  - Test computation: 5 * 2 = {computed_result}")


def test_dask_setup_with_file_config():
    """Test that Dask setup is successful when loading configuration from file."""
    # Create temporary config file
    config_data = {
        'n_workers': 1,
        'n_cores_per_worker': 1,
        'memory_limit': '1GB',
        'cluster_type': 'local'
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config_data, f)
        config_file = f.name
    
    try:
        # Test loading from file
        config = DaskConfig(config_file=config_file)
        assert config.n_workers == 1
        assert config.memory_limit == '1GB'
        
        # Test that setup works
        client = config.configure_dask()
        assert client is not None
        
        # Verify cluster is running
        scheduler_info = client.scheduler_info()
        assert len(scheduler_info['workers']) >= 1
        
        print(f"✓ Dask setup from file successful!")
        print(f"  - Dashboard: {client.dashboard_link}")
        print(f"  - Workers: {len(scheduler_info['workers'])}")
        
    finally:
        os.unlink(config_file)


def test_dask_setup_static_methods():
    """Test that Dask setup is successful using static methods."""
    # Test static method for getting current client
    client = DaskConfig.get_current_client()
    assert client is not None
    assert hasattr(client, 'dashboard_link')
    
    # Test static method for configuring from parameters
    parameters = {'dask_config': {'n_workers': 1, 'memory_limit': '1GB'}}
    client2 = DaskConfig.configure_from_parameters(parameters)
    assert client2 is not None
    
    # Verify both clients are working
    scheduler_info1 = client.scheduler_info()
    scheduler_info2 = client2.scheduler_info()
    
    assert len(scheduler_info1['workers']) >= 1
    assert len(scheduler_info2['workers']) >= 1
    
    print(f"✓ Dask setup with static methods successful!")
    print(f"  - Client 1 workers: {len(scheduler_info1['workers'])}")
    print(f"  - Client 2 workers: {len(scheduler_info2['workers'])}")


def test_dask_setup_computation_workflow():
    """Test that Dask setup supports actual computation workflows."""
    # Create a more complex configuration
    config = DaskConfig(
        n_workers=2,
        n_cores_per_worker=1,
        memory_limit="1GB",
        cluster_type="local"
    )
    
    client = config.configure_dask()
    assert client is not None
    
    # Test parallel computation
    from dask import delayed
    import dask
    
    @delayed
    def compute_square(x):
        time.sleep(0.1)  # Simulate some work
        return x ** 2
    
    @delayed
    def compute_sum(values):
        return sum(values)
    
    # Create a parallel computation
    numbers = list(range(1, 6))  # [1, 2, 3, 4, 5]
    squares = [compute_square(x) for x in numbers]
    total = compute_sum(squares)
    
    # Compute the result
    result = total.compute()
    expected = sum(x**2 for x in numbers)  # 1 + 4 + 9 + 16 + 25 = 55
    
    assert result == expected
    
    # Test that we can get configuration info
    info = config.get_config_info()
    assert 'cluster_type' in info
    assert 'n_workers' in info
    assert info['n_workers'] == 2
    
    print(f"✓ Dask computation workflow successful!")
    print(f"  - Dashboard: {client.dashboard_link}")
    print(f"  - Computation result: {result} (expected: {expected})")
    print(f"  - Workers: {info['n_workers']}")


def test_dask_setup_error_handling():
    """Test that Dask setup handles errors gracefully."""
    # Test with invalid configuration
    try:
        config = DaskConfig(
            n_workers=0,  # Invalid: 0 workers
            cluster_type="local"
        )
        # This should still work (will use default values)
        client = config.configure_dask()
        assert client is not None
        print("✓ Dask setup handles invalid config gracefully")
    except Exception as e:
        pytest.fail(f"Dask setup should handle invalid config gracefully, but got: {e}")
    
    # Test with non-existent config file
    try:
        config = DaskConfig(config_file="non_existent_file.yaml")
        pytest.fail("Should have raised FileNotFoundError for non-existent file")
    except FileNotFoundError:
        print("✓ Dask setup correctly handles missing config file")
    except Exception as e:
        pytest.fail(f"Expected FileNotFoundError, but got: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
