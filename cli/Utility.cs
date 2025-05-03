using System.Linq;
using Microsoft.Dafny;

namespace DafnySketcherCli {
  public static class Utility {
    public static Method? GetMethodByName(Microsoft.Dafny.Program prog, string name) {
      return prog.DefaultModuleDef
        .TopLevelDecls
        .OfType<TopLevelDeclWithMembers>()
        .SelectMany(d => d.Members.OfType<Method>())
        .FirstOrDefault(m => m.Name == name);
    }

    public static Method GetEnclosingMethodByPosition(Microsoft.Dafny.Program resolvedProgram, int line, int col) {
      //Log("# Getting Method");
      if (resolvedProgram.DefaultModuleDef is DefaultModuleDefinition defaultModule) {
        foreach (var topLevelDecl in defaultModule.TopLevelDecls) {
          if (topLevelDecl is TopLevelDeclWithMembers classDecl) {
            foreach (var member in classDecl.Members) {
              var method = member as Method;
              if (method != null) {
                //var methodDetails = $"lines {method.Tok.line}-{method.EndToken.line}";
                if (IsPositionInRange(method.StartToken, method.EndToken, line, col)) {
                  //Log("## Found method: " + methodDetails);
                  return method;
                } else {
                  //Log("## Method out of range: " + methodDetails);
                }
              }
            }
          }
        }
      }
      return null;
    }
    private static bool IsPositionInRange(IOrigin startToken, IOrigin endToken, int line, int col) {
      return line >= startToken.line && line <= endToken.line &&
            (line != startToken.line || col >= startToken.col) &&
            (line != endToken.line || col <= endToken.col);
    }
  }
}