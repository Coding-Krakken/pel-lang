"""
PEL Visualization Module

Generates charts and visualizations from PEL simulation results:
- Time series line charts
- Distribution histograms
- Tornado charts (sensitivity analysis)
- Correlation matrices

Outputs: PNG, SVG, or base64-encoded images for HTML embedding
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    import seaborn as sns
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
    print("Warning: matplotlib/seaborn not installed. Install with: pip install matplotlib seaborn")


class ModelVisualizer:
    """Generates charts from PEL simulation results."""
    
    def __init__(self, results: Dict[str, Any]):
        """
        Initialize visualizer with simulation results.
        
        Args:
            results: PEL simulation results (from pel run output JSON)
        """
        if not VISUALIZATION_AVAILABLE:
            raise ImportError("Visualization requires matplotlib and seaborn. Install with: pip install matplotlib seaborn")
        
        self.results = results
        self.model_name = results.get("model", {}).get("name", "Unknown Model")
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (10, 6)
        plt.rcParams['font.size'] = 10
    
    def plot_time_series(
        self, 
        variable: str, 
        output_path: Optional[Path] = None,
        show_ci: bool = False
    ) -> Optional[Path]:
        """
        Plot a time series variable.
        
        Args:
            variable: Name of variable to plot
            output_path: Path to save chart (PNG)
            show_ci: Whether to show confidence intervals (Monte Carlo only)
            
        Returns:
            Path to saved chart, or None if not saved
        """
        variables = self.results.get("variables", {})
        
        if variable not in variables:
            raise ValueError(f"Variable '{variable}' not found in results")
        
        values = variables[variable]
        
        if not isinstance(values, list):
            raise ValueError(f"Variable '{variable}' is not a time series")
        
        fig, ax = plt.subplots()
        
        timesteps = list(range(len(values)))
        ax.plot(timesteps, values, marker='o', linewidth=2, markersize=4)
        
        ax.set_xlabel('Timestep')
        ax.set_ylabel(variable)
        ax.set_title(f'{variable} Over Time - {self.model_name}')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.close()
            return None
    
    def plot_distribution(
        self,
        variable: str,
        output_path: Optional[Path] = None,
        show_percentiles: bool = True
    ) -> Optional[Path]:
        """
        Plot distribution of a variable (Monte Carlo results).
        
        Args:
            variable: Name of variable to plot
            output_path: Path to save chart (PNG)
            show_percentiles: Whether to show p50/p95 lines
            
        Returns:
            Path to saved chart, or None if not saved
        """
        # Placeholder for Monte Carlo distribution visualization
        # Requires aggregated results from multiple runs
        raise NotImplementedError("Distribution plots require Monte Carlo aggregation - coming soon")
    
    def plot_tornado(
        self,
        sensitivities: Dict[str, float],
        output_path: Optional[Path] = None
    ) -> Optional[Path]:
        """
        Plot tornado chart for sensitivity analysis.
        
        Args:
            sensitivities: Dict mapping parameter names to sensitivity values
            output_path: Path to save chart (PNG)
            
        Returns:
            Path to saved chart, or None if not saved
        """
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Sort by absolute sensitivity
        sorted_items = sorted(sensitivities.items(), key=lambda x: abs(x[1]), reverse=True)
        params = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]
        
        # Create horizontal bar chart
        y_pos = range(len(params))
        colors = ['#e74c3c' if v < 0 else '#27ae60' for v in values]
        
        ax.barh(y_pos, values, color=colors, alpha=0.7)
        ax.set_yticks(y_pos)
        ax.set_yticklabels(params)
        ax.set_xlabel('Sensitivity')
        ax.set_title(f'Sensitivity Analysis - {self.model_name}')
        ax.axvline(x=0, color='black', linewidth=0.8)
        ax.grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')
            plt.close()
            return output_path
        else:
            plt.close()
            return None
    
    def create_all_charts(self, output_dir: Path) -> List[Path]:
        """
        Generate all available charts for the model.
        
        Args:
            output_dir: Directory to save charts
            
        Returns:
            List of paths to generated charts
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []
        
        # Generate time series for all variables
        variables = self.results.get("variables", {})
        for var_name, values in variables.items():
            if isinstance(values, list) and len(values) > 1:
                try:
                    chart_path = output_dir / f"{var_name}_timeseries.png"
                    self.plot_time_series(var_name, chart_path)
                    generated.append(chart_path)
                except Exception as e:
                    print(f"Warning: Could not generate chart for {var_name}: {e}")
        
        return generated


def visualize_results(
    results_path: Path,
    output_dir: Path,
    chart_types: Optional[List[str]] = None
) -> List[Path]:
    """
    Convenience function to generate visualizations from results file.
    
    Args:
        results_path: Path to PEL simulation results JSON
        output_dir: Directory to save charts
        chart_types: Optional list of chart types to generate
        
    Returns:
        List of paths to generated charts
    """
    with open(results_path) as f:
        results = json.load(f)
    
    viz = ModelVisualizer(results)
    return viz.create_all_charts(output_dir)


if __name__ == "__main__":
    # Simple CLI for testing
    import sys
    if len(sys.argv) < 3:
        print("Usage: python visualization.py <results.json> <output_dir>")
        sys.exit(1)
    
    results_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    charts = visualize_results(results_path, output_dir)
    print(f"Generated {len(charts)} charts in {output_dir}")
    for chart in charts:
        print(f"  - {chart.name}")
