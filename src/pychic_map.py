import matplotlib.pyplot as plt
import osmnx as ox
from helpers import check_ox_version
import argparse
from shapely.geometry import box
from shapely.geometry import Point
import geopandas as gpd

class PyChicMapper():
    
    def __init__(self, args):
        lat = round(float(args.lat), 4)
        lon = round(float(args.lon), 4)
        center_point = (lat, lon)
        self.radius = int(args.radius)
        # import pdb 
        # pdb.set_trace()
        # gather data from the OSMNX
        self.G = ox.graph_from_point(center_point, dist=self.radius, network_type="drive")
        self.nodes_gdf, self.edges_gdf = ox.graph_to_gdfs(self.G)
        
        self.add_river = args.river
        self.output_image =args.output  if args.output else "./image.png"
        self.dpi  = args.dpi if args.dpi else 400
        
        if self.add_river:
            self.river_G = ox.graph_from_point(center_point, dist=self.radius, network_type="drive", custom_filter='["waterway"~"river"]')
            # Convert the graph edges to a GeoDataFrame
            self.river_nodes_gdf, self.river_edges_gdf = ox.graph_to_gdfs(self.river_G)
        
        self.shape = args.shape
        
    def generate_box(self):
        combined_bounds = self.edges_gdf.total_bounds  # [minx, miny, maxx, maxy]
        # Calculate width and height of the network's bounding box
        net_width = combined_bounds[2] - combined_bounds[0]
        net_height = combined_bounds[3] - combined_bounds[1]
        
        target_aspect = 5 / 7
        # Determine new height and width while maintaining the target aspect ratio
        if (net_width / net_height) > target_aspect:
            print(f"Network is too wide, adjust width")
            new_width = net_height * target_aspect
            new_height = net_height
        else:
            print("Network is too tall, adjust height")
            new_height = net_width / target_aspect
            new_width = net_width

        # Calculate the new bbox, centered on the network
        center_x, center_y = (combined_bounds[0] + combined_bounds[2]) / 2, (combined_bounds[1] + combined_bounds[3]) / 2
        bbox = box(center_x - new_width / 2, center_y - new_height / 2, center_x + new_width / 2, center_y + new_height / 2)
        
        return bbox
    
    def generate_circle():
        pass
        
    def generate_map(self):
        if self.shape =="box":
            map_shape = self.generate_box()
        elif self.shape == "circle":
            map_shape = self.generate_circle()
        else:
            raise("Provide valid shape, only box and circle are supported now.")
    
                
        # Clip the edges and river edges to the bounding box
        edges_cropped = self.edges_gdf.clip(map_shape)
        G_clipped = ox.graph_from_gdfs(self.nodes_gdf, edges_cropped)

        # Plot using ox.plot_graph for the clipped graph
        fig, ax = plt.subplots(figsize=(5, 7))
        ox.plot_graph(
            G_clipped,
            ax=ax,
            show=False,
            close=False,
            bgcolor="#ffffff",
            edge_color="black",
            edge_linewidth=0.3,
            node_size=0,
            dpi=self.dpi
        )

        
        if self.add_river:
            river_edges_cropped = self.river_edges_gdf.clip(map_shape)
            river_G_clipped = ox.graph_from_gdfs(self.river_nodes_gdf, river_edges_cropped)
            ox.plot_graph(
                river_G_clipped,
                ax=ax,
                show=False,
                close=False,
                bgcolor="#ffffff",
                edge_color="#0a95a9",
                edge_linewidth=1.9,
                node_size=0,
                dpi=self.dpi
            )

        # Clean up the plot appearance
        ax.set_axis_off()
        plt.axis('equal')

        # Save the cropped map
        plt.savefig(self.output_image, dpi=400, bbox_inches='tight', transparent=False, pad_inches=0)
        # plt.show()



def main(args):
    check_ox_version()
    mapper = PyChicMapper(args)
    mapper.generate_map()
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-lat", "--lat", required=True, help="latitude of the place")
    parser.add_argument("-lon", "--lon", required=True, help="longitude of the place")
    parser.add_argument("-radius", "--radius", required=True, help="radius of the map in meters")
    parser.add_argument("-shape", "--shape", required=False, help= "shape of map, only box and circle are suported")
    parser.add_argument("-river", "--river", required=False,type=bool, help= "include river or not")
    parser.add_argument("-output", "--output", required=False, help= "output path of the image , default ./image.png")
    parser.add_argument("-dpi", "--dpi", required=False, help= "dpi of the output image")
    args = parser.parse_args()
    main(args)