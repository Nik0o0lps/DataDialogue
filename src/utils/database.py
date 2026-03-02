"""
Utilitários para trabalhar com o banco de dados SQLite.
"""
import sqlite3
from typing import List, Dict, Any, Tuple
import pandas as pd


class DatabaseManager:
    """Gerencia conexões e operações com o banco de dados."""
    
    def __init__(self, db_path: str = "anexo_desafio_1.db"):
        self.db_path = db_path
    
    def get_connection(self) -> sqlite3.Connection:
        """Cria uma nova conexão com o banco de dados."""
        return sqlite3.connect(self.db_path)
    
    def get_schema(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retorna o schema completo do banco de dados.
        
        Returns:
            Dicionário com nomes de tabelas como chaves e suas colunas como valores
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Obter todas as tabelas (exceto sqlite_sequence)
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name != 'sqlite_sequence'
            ORDER BY name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        
        schema = {}
        for table_name in tables:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema[table_name] = []
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, pk = col
                schema[table_name].append({
                    'name': col_name,
                    'type': col_type,
                    'primary_key': bool(pk),
                    'not_null': bool(not_null)
                })
        
        conn.close()
        return schema
    
    def get_schema_text(self) -> str:
        """
        Retorna o schema em formato texto legível para o LLM.
        
        Returns:
            String com o schema formatado
        """
        schema = self.get_schema()
        text_parts = []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for table_name, columns in schema.items():
            text_parts.append(f"\nTabela: {table_name}")
            text_parts.append("Colunas:")
            for col in columns:
                pk_str = " (PRIMARY KEY)" if col['primary_key'] else ""
                not_null_str = " NOT NULL" if col['not_null'] else ""
                text_parts.append(f"  - {col['name']}: {col['type']}{pk_str}{not_null_str}")
            
            # Adicionar contagem de registros
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            text_parts.append(f"Total de registros: {count}")
            
            # Adicionar exemplos de valores para colunas categóricas importantes
            categorical_columns = {
                'compras': ['canal', 'categoria'],
                'clientes': ['estado'],
                'suporte': ['canal_interacao', 'tipo'],
                'campanhas_marketing': ['canal_campanha', 'tipo_campanha']
            }
            
            if table_name in categorical_columns:
                for col_name in categorical_columns[table_name]:
                    # Verificar se a coluna existe
                    col_exists = any(c['name'] == col_name for c in columns)
                    if col_exists:
                        try:
                            cursor.execute(f"SELECT DISTINCT {col_name} FROM {table_name} WHERE {col_name} IS NOT NULL LIMIT 10")
                            values = [str(row[0]) for row in cursor.fetchall()]
                            if values:
                                text_parts.append(f"Valores distintos de {col_name}: {', '.join(values)}")
                        except Exception:
                            pass  # Ignorar se houver erro
            
            # Adicionar informações sobre range de datas se houver coluna de data
            date_columns = [col['name'] for col in columns if 'data' in col['name'].lower()]
            for date_col in date_columns:
                try:
                    cursor.execute(f"SELECT MIN({date_col}), MAX({date_col}) FROM {table_name} WHERE {date_col} IS NOT NULL")
                    min_date, max_date = cursor.fetchone()
                    if min_date and max_date:
                        text_parts.append(f"Range de {date_col}: {min_date} a {max_date}")
                except Exception:
                    pass  # Ignorar se houver erro
        
        conn.close()
        
        return "\n".join(text_parts)
    
    def execute_query(self, query: str) -> Tuple[bool, Any]:
        """
        Executa uma query SQL e retorna os resultados.
        
        Args:
            query: Query SQL para executar
            
        Returns:
            Tupla (sucesso, resultado ou mensagem de erro)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Executar a query
            cursor.execute(query)
            
            # Verificar se é SELECT (retorna dados) ou outra operação
            if query.strip().upper().startswith('SELECT'):
                columns = [description[0] for description in cursor.description]
                rows = cursor.fetchall()
                
                # Retornar como DataFrame do pandas
                df = pd.DataFrame(rows, columns=columns)
                conn.close()
                return True, df
            else:
                # Para INSERT, UPDATE, DELETE, etc.
                conn.commit()
                affected_rows = cursor.rowcount
                conn.close()
                return True, f"Operação executada com sucesso. {affected_rows} linhas afetadas."
                
        except sqlite3.Error as e:
            return False, f"Erro SQL: {str(e)}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
    
    def get_sample_data(self, table_name: str, limit: int = 3) -> pd.DataFrame:
        """
        Retorna alguns registros de exemplo de uma tabela.
        
        Args:
            table_name: Nome da tabela
            limit: Número de registros para retornar
            
        Returns:
            DataFrame com os dados de exemplo
        """
        query = f"SELECT * FROM {table_name} LIMIT {limit}"
        success, result = self.execute_query(query)
        
        if success:
            return result
        else:
            return pd.DataFrame()
