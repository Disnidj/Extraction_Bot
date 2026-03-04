"""
Portal mapping service - fetches broker-portal relationships from database.
"""

from typing import List, Dict, Set, Tuple
from src.services.db_config.db_connect import MySQLDatabase
from src.services.db_config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD
from src.config.broker_config import get_broker_name


class PortalMapper:
    """Manages broker-portal mappings from database."""
    
    def __init__(self):
        self.db = MySQLDatabase(DB_HOST, DB_NAME, DB_USER, DB_PASSWORD)
    
    def fetch_portals_for_broker(self, broker_id: int) -> List[str]:
        """
        Fetch portals for a specific broker from database.
        
        Args:
            broker_id: Broker ID
            
        Returns:
            List of portal names
        """
        query = """
            SELECT DISTINCT Portal_Name
            FROM Medical_CTN_Broker_Portal_Mapping
            WHERE Broker_ID = %s
            ORDER BY Portal_Name
        """
        
        if not self.db.connect():
            raise ConnectionError("Failed to connect to database")
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(query, (broker_id,))
            results = cursor.fetchall()
            return [row[0] for row in results]
        finally:
            cursor.close()
            self.db.disconnect()
    
    def fetch_portals_for_multiple_brokers(self, broker_ids: List[int]) -> Dict[int, List[str]]:
        """
        Fetch portals for multiple brokers.
        
        Args:
            broker_ids: List of broker IDs
            
        Returns:
            Dict mapping broker_id -> list of portal names
            
        Example:
            {
                3: ['ADNIC', 'Takaful', 'MaxHealth'],
                6: ['ADNIC', 'AL SAGR']
            }
        """
        broker_portals = {}
        
        for broker_id in broker_ids:
            portals = self.fetch_portals_for_broker(broker_id)
            broker_portals[broker_id] = portals
        
        return broker_portals
    
    def get_unique_portals(self, broker_ids: List[int]) -> List[str]:
        """
        Get deduplicated list of portals across all brokers.
        
        Args:
            broker_ids: List of broker IDs
            
        Returns:
            Sorted list of unique portal names
        """
        all_portals = set()
        
        for broker_id in broker_ids:
            portals = self.fetch_portals_for_broker(broker_id)
            all_portals.update(portals)
        
        return sorted(all_portals)
    
    def analyze_portal_distribution(self, broker_ids: List[int]) -> Dict:
        """
        Analyze portal distribution across brokers.
        
        Args:
            broker_ids: List of broker IDs
            
        Returns:
            Dict with portal analysis:
            {
                'total_unique': 10,
                'shared': {
                    'ADNIC': [3, 6],
                    'AL SAGR': [3, 6]
                },
                'unique': {
                    'Takaful': 3,
                    'MaxHealth': 3
                },
                'broker_counts': {
                    3: 8,
                    6: 3
                }
            }
        """
        broker_portals = self.fetch_portals_for_multiple_brokers(broker_ids)
        
        # Count portal occurrences
        portal_to_brokers = {}
        for broker_id, portals in broker_portals.items():
            for portal in portals:
                if portal not in portal_to_brokers:
                    portal_to_brokers[portal] = []
                portal_to_brokers[portal].append(broker_id)
        
        # Separate shared vs unique portals
        shared = {}
        unique = {}
        
        for portal, broker_list in portal_to_brokers.items():
            if len(broker_list) > 1:
                shared[portal] = broker_list
            else:
                unique[portal] = broker_list[0]
        
        return {
            'total_unique': len(portal_to_brokers),
            'shared': shared,
            'unique': unique,
            'broker_counts': {bid: len(portals) for bid, portals in broker_portals.items()},
            'all_portals': sorted(portal_to_brokers.keys())
        }
    
    def get_portal_summary_text(self, broker_ids: List[int]) -> str:
        """
        Get human-readable portal summary.
        
        Args:
            broker_ids: List of broker IDs
            
        Returns:
            Formatted summary string
        """
        analysis = self.analyze_portal_distribution(broker_ids)
        
        summary = f"Total Unique Portals: {analysis['total_unique']}\n\n"
        
        if analysis['shared']:
            summary += f"Shared Portals ({len(analysis['shared'])}):\n"
            for portal, broker_list in analysis['shared'].items():
                broker_names = [f"Broker {bid}" for bid in broker_list]
                summary += f"  • {portal} → {', '.join(broker_names)}\n"
            summary += "\n"
        
        if analysis['unique']:
            summary += f"Broker-Specific Portals ({len(analysis['unique'])}):\n"
            for portal, broker_id in analysis['unique'].items():
                summary += f"  • {portal} → Broker {broker_id} - {get_broker_name(broker_id)}\n"
        
        return summary
    
    def get_brokers_using_portal(self, portal_name: str) -> List[int]:
        """
        Find which brokers use a specific portal.
        
        Args:
            portal_name: Portal name to search
            
        Returns:
            List of broker IDs using this portal
        """
        query = """
            SELECT DISTINCT Broker_ID
            FROM Medical_CTN_Broker_Portal_Mapping
            WHERE Portal_Name = %s
            ORDER BY Broker_ID
        """
        
        if not self.db.connect():
            raise ConnectionError("Failed to connect to database")
        
        try:
            cursor = self.db.connection.cursor()
            cursor.execute(query, (portal_name,))
            results = cursor.fetchall()
            return [row[0] for row in results]
        finally:
            cursor.close()
            self.db.disconnect()
