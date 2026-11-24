import hashlib
import secrets
from typing import Optional, Dict, Any, List, Tuple
import sqlite3

def hash_password(password: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """
    Gera o hash da senha usando PBKDF2 HMAC SHA-256 com salt aleatório.
    Garante segurança robusta sem necessidade de dependências C externas.
    """
    if not salt:
        salt = secrets.token_hex(16)
    
    hashed = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    
    return hashed, salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """Verifica se a senha fornecida coincide com o hash armazenado."""
    calculated_hash, _ = hash_password(password, salt)
    return secrets.compare_digest(calculated_hash, stored_hash)

def autenticar_usuario(db_conn: sqlite3.Connection, username: str, password: str) -> Optional[Dict[str, Any]]:
    """
    Autentica um usuário pelo nome de usuário e senha.
    Retorna o dicionário com os dados do usuário ou None se inválido/inativo.
    """
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT id, nome, username, password_hash, salt, perfil, ativo
        FROM usuarios
        WHERE LOWER(username) = LOWER(?)
    """, (username.strip(),))
    
    row = cursor.fetchone()
    if not row:
        return None
    
    user = dict(row)
    if not user.get("ativo", 1):
        return {"erro": "usuario_inativo"}
    
    if verify_password(password, user["password_hash"], user["salt"]):
        # Retorna dados sem os segredos
        return {
            "id": user["id"],
            "nome": user["nome"],
            "username": user["username"],
            "perfil": user["perfil"]
        }
    
    return None

def cadastrar_usuario(db_conn: sqlite3.Connection, nome: str, username: str, password: str, perfil: str) -> Tuple[bool, str]:
    """
    Cadastra um novo usuário no sistema com senha hasheada.
    """
    nome = nome.strip()
    username = username.strip().lower()
    
    if not nome:
        return False, "O nome do usuário é obrigatório."
    if not username or len(username) < 3:
        return False, "O nome de usuário deve conter pelo menos 3 caracteres."
    if not password or len(password) < 4:
        return False, "A senha deve ter pelo menos 4 caracteres."
    if perfil not in ("administrador", "funcionario"):
        return False, "Nível de acesso inválido. Selecione 'administrador' ou 'funcionario'."
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT id FROM usuarios WHERE LOWER(username) = ?", (username,))
    if cursor.fetchone():
        return False, f"O usuário '{username}' já existe no sistema."
    
    p_hash, salt = hash_password(password)
    
    try:
        cursor.execute("""
            INSERT INTO usuarios (nome, username, password_hash, salt, perfil, ativo)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (nome, username, p_hash, salt, perfil))
        db_conn.commit()
        return True, f"Usuário '{username}' cadastrado com sucesso!"
    except Exception as e:
        db_conn.rollback()
        return False, f"Erro ao cadastrar usuário: {str(e)}"

def listar_usuarios(db_conn: sqlite3.Connection) -> List[Dict[str, Any]]:
    """Lista todos os usuários para visualização do administrador."""
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT id, nome, username, perfil, ativo, criado_em
        FROM usuarios
        ORDER BY nome ASC
    """)
    return [dict(r) for r in cursor.fetchall()]

def alternar_status_usuario(db_conn: sqlite3.Connection, user_id: int, admin_atual_id: int) -> Tuple[bool, str]:
    """Ativa ou desativa um usuário, impedindo auto-desativação do admin atual."""
    if user_id == admin_atual_id:
        return False, "Você não pode desativar o seu próprio usuário logado."
    
    cursor = db_conn.cursor()
    cursor.execute("SELECT ativo, username FROM usuarios WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        return False, "Usuário não encontrado."
    
    novo_status = 0 if user["ativo"] == 1 else 1
    cursor.execute("UPDATE usuarios SET ativo = ? WHERE id = ?", (novo_status, user_id))
    db_conn.commit()
    
    status_label = "ativado" if novo_status == 1 else "desativado"
    return True, f"Usuário '{user['username']}' {status_label} com sucesso!"

def redefinir_senha_usuario(db_conn: sqlite3.Connection, user_id: int, nova_senha: str) -> Tuple[bool, str]:
    """Redefine a senha de um usuário."""
    if not nova_senha or len(nova_senha) < 4:
        return False, "A nova senha deve ter pelo menos 4 caracteres."
    
    p_hash, salt = hash_password(nova_senha)
    cursor = db_conn.cursor()
    cursor.execute("""
        UPDATE usuarios
        SET password_hash = ?, salt = ?
        WHERE id = ?
    """, (p_hash, salt, user_id))
    db_conn.commit()
    return True, "Senha redefinida com sucesso!"
