module Main where

import Text.ParserCombinators.Parsec 
import System.IO
import System.Directory

number :: Parser Integer
number = do
	ds <- many1 digit
	return (read ds)

entry :: Parser (String, Bool)
entry = do
	cs <- many (noneOf " ")
	spaces
	n <- number
	spaces
	ns <- sepEndBy1 number (skipMany1 space)
	return (cs, n * 4 == toInteger (length ns))

run :: Parser (String, Bool) -> String -> IO Bool
run p input = case (parse p "" input) of
	Left err -> do
					putStr "parse error at "
					print err 
					return False
	Right (fpath, x) -> do
				if x
				then putStr ""
				else putStr ("wrong number of regions in " ++ fpath)
				be <- doesFileExist fpath
				if be
				then putStr ""
				else putStr (fpath ++ " does NOT exist")
				return x


-- runghc validate.hs < info.dat
main = do
	--run entry "pos/img_-JjVDyhQ4AL4vemn1rja.png 12 1 2 3 4"
	--cs <- getLine
	--run entry cs
	getContents >>= mapM_ (run entry) . lines
