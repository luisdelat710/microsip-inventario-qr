-- Existencias por artículo desde la base Firebird de Microsip.
-- Basado en el esquema típico de Microsip (ARTICULOS, CLAVES_ARTICULOS, SALDOS_IN).
-- Verifica nombres de tablas y campos contra tu versión antes de usarlo.
--
-- SALDOS_IN guarda entradas y salidas acumuladas por artículo, almacén y periodo;
-- la existencia es la suma de (entradas - salidas) en todos los periodos.

SELECT
    ca.CLAVE_ARTICULO              AS CLAVE,
    a.NOMBRE                       AS NOMBRE,
    a.UNIDAD_VENTA                 AS UNIDAD,
    SUM(s.ENTRADAS_UNIDADES - s.SALIDAS_UNIDADES) AS EXISTENCIA
FROM ARTICULOS a
JOIN SALDOS_IN s
      ON s.ARTICULO_ID = a.ARTICULO_ID
LEFT JOIN CLAVES_ARTICULOS ca
      ON ca.ARTICULO_ID = a.ARTICULO_ID
WHERE a.ESTATUS = 'A'
  AND s.ALMACEN_ID = ?
GROUP BY ca.CLAVE_ARTICULO, a.NOMBRE, a.UNIDAD_VENTA
HAVING SUM(s.ENTRADAS_UNIDADES - s.SALIDAS_UNIDADES) <> 0
ORDER BY a.NOMBRE
