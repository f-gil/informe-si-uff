import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()


class KeysManager:
    """Gerencia múltiplas chaves de API Gemini com round-robin."""

    def __init__(self):
        """Carrega todas as chaves de ambiente dinamicamente."""
        self.keys = self._carregar_chaves()
        self.indice_atual = 0

        if not self.keys:
            raise ValueError(
                "❌ Nenhuma chave Gemini encontrada! Configure no .env:\n"
                "   GEMINI_API_KEY_1=xxx\n"
                "   GEMINI_API_KEY_2=yyy\n"
                "   etc..."
            )

        logger.info(f"🔑 {len(self.keys)} chave(s) Gemini carregada(s)")

    def _carregar_chaves(self):
        """
        Carrega dinamicamente todas as chaves do formato:
        GEMINI_API_KEY_1, GEMINI_API_KEY_2, ...

        Returns:
            lista de chaves válidas
        """
        chaves = []
        indice = 1

        # Procura por GEMINI_API_KEY_1, _2, _3, etc até não encontrar mais
        while True:
            chave_var = f"GEMINI_API_KEY_{indice}"
            chave_valor = os.getenv(chave_var)

            if not chave_valor:
                break  # Parou de encontrar chaves

            chaves.append(chave_valor.strip())
            logger.debug(f"  ✓ Chave {indice} carregada")
            indice += 1

        return chaves

    def obter_proxima_chave(self):
        """
        Retorna a próxima chave em sequência (round-robin).

        Returns:
            (chave, numero_chave) - string da chave e seu índice (1-based)
        """
        chave = self.keys[self.indice_atual]
        numero = self.indice_atual + 1  # 1-based para logs mais legíveis

        # Avança para próxima (com wrap-around)
        self.indice_atual = (self.indice_atual + 1) % len(self.keys)

        logger.debug(f"🔑 Usando chave #{numero}/{len(self.keys)}")
        return chave, numero

    def obter_chave_especifica(self, numero):
        """
        Obtém uma chave específica por número (1-based).

        Args:
            numero: número da chave (1, 2, 3, ...)

        Returns:
            chave string ou None se não existe
        """
        indice = numero - 1  # Converter para 0-based
        if 0 <= indice < len(self.keys):
            return self.keys[indice]
        return None

    def obter_total_chaves(self):
        """Retorna quantas chaves estão configuradas."""
        return len(self.keys)

    def resetar_indice(self):
        """Reseta o round-robin (útil para testes)."""
        self.indice_atual = 0
        logger.debug("🔄 Índice de chaves resetado")

    def rotacionar_para_proxima(self):
        """
        Força rotação para próxima chave (útil quando uma falha).

        Returns:
            numero_nova_chave
        """
        logger.warning(f"⚠️ Chave #{self.indice_atual + 1} descartada, usando próxima...")
        _, numero = self.obter_proxima_chave()
        return numero

    def info(self):
        """Retorna informações sobre as chaves carregadas."""
        return {
            "total_chaves": len(self.keys),
            "indice_atual": self.indice_atual + 1,
            "proxima_chave": (self.indice_atual + 1) % len(self.keys) + 1,
        }


# Singleton global
_keys_manager = None


def get_keys_manager():
    """Retorna instância única do KeysManager."""
    global _keys_manager
    if _keys_manager is None:
        _keys_manager = KeysManager()
    return _keys_manager
