import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
from shapely.geometry import Point
import pandas as pd

def produce_mine_image(points, scores, centre, size_km=11, crs="EPSG:27700", save_path="mine_map.png"):
    """
    Create an image with points colour-coded by score and clipped to a square extent around a centre point.

    Args:
        points (list of tuple): [(x, y), ...] coordinates
        scores (list of float): Scores between 0-100
        centre (tuple): (x, y) coordinate for map centre
        size_km (float): Length of the square side in km (default 11)
        crs (str): CRS of input points and centre
        save_path (str): File path to save the map image
    """
    # Build GeoDataFrame
    gdf = gpd.GeoDataFrame({
        "score": scores,
        "geometry": [Point(x, y) for x, y in points]
    }, crs=crs)

    # Convert to Web Mercator for plotting with basemap
    gdf_web = gdf.to_crs(epsg=3857)

    # Centre in same CRS
    centre_point = gpd.GeoSeries([Point(centre)], crs=crs).to_crs(epsg=3857).iloc[0]
    cx, cy = centre_point.x, centre_point.y

    # Calculate half-size in metres (Web Mercator is in m)
    half_size = (size_km * 1000) / 2

    # Plot
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_web.plot(
        ax=ax,
        column="score",
        marker="*",
        markersize=150,
        cmap="RdYlGn",
        legend=True,
        legend_kwds={'label': "Suitability Score", 'shrink': 0.6}
    )

    # Fix extent to square around centre
    ax.set_xlim(cx - half_size, cx + half_size)
    ax.set_ylim(cy - half_size, cy + half_size)

    # Add basemap
    ctx.add_basemap(ax, crs=gdf_web.crs, source=ctx.providers.Esri.WorldStreetMap, alpha=0.75)

    ax.set_axis_off()
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close(fig)

# Example
points = [(421071.26, 564887.786), (420500, 564000), (421500, 565500)]
scores = [80, 45, 95]
centre = (421071.26, 564887.786)
produce_mine_image(points, scores, centre, size_km=11)
