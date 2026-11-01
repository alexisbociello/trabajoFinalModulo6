import Foundation
import AppKit
import CoreText
import PDFKit

struct Block: Decodable { let heading: String; let text: String }
struct Page: Decodable { let title: String; let subtitle: String; let blocks: [Block]; let kind: String }
let root = URL(fileURLWithPath: FileManager.default.currentDirectoryPath)
let src = root.appendingPathComponent("08_Informe/01_Borradores/fuentes_pdf/paginas.json")
let pages = try JSONDecoder().decode([Page].self, from: Data(contentsOf: src))
let output = root.appendingPathComponent("08_Informe/03_PDF_final/Informe_Final_Modulo6_Individual.pdf")
var media = CGRect(x: 0, y: 0, width: 595.28, height: 841.89)
let ctx = CGContext(output as CFURL, mediaBox: &media, nil)!
func color(_ r: CGFloat,_ g: CGFloat,_ b: CGFloat) -> NSColor { NSColor(calibratedRed:r,green:g,blue:b,alpha:1) }
let ink = color(0.12,0.19,0.25), teal = color(0.02,0.40,0.43)
func drawText(_ text: String, x: CGFloat, top: CGFloat, width: CGFloat, size: CGFloat, bold: Bool = false, tint: NSColor = ink, spacing: CGFloat = 3) -> CGFloat {
    let para = NSMutableParagraphStyle(); para.lineSpacing = spacing
    let attrs: [NSAttributedString.Key:Any] = [.font: NSFont.systemFont(ofSize:size,weight:bold ? .semibold : .regular), .foregroundColor:tint, .paragraphStyle:para]
    let value = NSAttributedString(string:text,attributes:attrs)
    let fs = CTFramesetterCreateWithAttributedString(value)
    let fit = CTFramesetterSuggestFrameSizeWithConstraints(fs,CFRange(location:0,length:0),nil,CGSize(width:width,height:10000),nil)
    let height = ceil(fit.height)+3
    let rect = CGRect(x:x,y:media.height-top-height,width:width,height:height)
    let frame = CTFramesetterCreateFrame(fs,CFRange(location:0,length:0),CGPath(rect:rect,transform:nil),nil)
    let visible = CTFrameGetVisibleStringRange(frame)
    if visible.length != value.length { fatalError("Texto incompleto") }
    CTFrameDraw(frame,ctx)
    return height
}
for (index,page) in pages.enumerated() {
    ctx.beginPDFPage(nil)
    ctx.setFillColor(color(0.97,0.98,0.98).cgColor);ctx.fill(CGRect(x:0,y:media.height-144,width:media.width,height:144))
    ctx.setFillColor(teal.cgColor);ctx.fill(CGRect(x:42,y:media.height-42,width:34,height:4))
    var y: CGFloat = 57
    y += drawText("MÓDULO 6  /  INGENIERÍA DE DATOS Y MLOPS",x:42,top:y,width:510,size:9,bold:true,tint:teal)
    y += 10
    y += drawText(page.title,x:42,top:y,width:511,size:page.kind == "cover" ? 29 : 23,bold:true,spacing:2)
    y += 5
    y += drawText(page.subtitle,x:42,top:y,width:511,size:10,tint:color(0.38,0.44,0.49),spacing:2)
    y = max(y+27,166)
    for block in page.blocks {
        y += drawText(block.heading,x:42,top:y,width:511,size:11.4,bold:true,tint:teal,spacing:2)
        y += 5
        y += drawText(block.text,x:42,top:y,width:511,size:10.3,spacing:3)
        y += 17
    }
    if y > 780 { fatalError("Desborde página \(index+1): \(y)") }
    ctx.setStrokeColor(color(0.8,0.85,0.86).cgColor);ctx.move(to:CGPoint(x:42,y:45));ctx.addLine(to:CGPoint(x:553,y:45));ctx.strokePath()
    _ = drawText("COMERCIAL HORIZONTE · INFORME TÉCNICO",x:42,top:805,width:440,size:8,tint:color(0.4,0.45,0.48))
    _ = drawText("\(index+1) / \(pages.count)",x:510,top:805,width:45,size:8,tint:color(0.4,0.45,0.48))
    ctx.endPDFPage()
    print("Página \(index+1): contenido hasta y=\(Int(y))")
}
ctx.closePDF()
let pdf = PDFDocument(url:output)!
let render = root.appendingPathComponent("tmp/pdfs/revision_informe")
try FileManager.default.createDirectory(at:render,withIntermediateDirectories:true)
let thumbW=CGFloat(298),thumbH=CGFloat(421)
let contact=NSImage(size:NSSize(width:thumbW*3,height:thumbH*3))
contact.lockFocus();NSColor.white.setFill();NSRect(x:0,y:0,width:thumbW*3,height:thumbH*3).fill()
for i in 0..<pdf.pageCount {
 let page=pdf.page(at:i)!
 let thumb=page.thumbnail(of:NSSize(width:1190,height:1684),for:.mediaBox)
 let data=NSBitmapImageRep(data:thumb.tiffRepresentation!)!.representation(using:.png,properties:[:])!
 try data.write(to:render.appendingPathComponent("pagina_\(i+1).png"))
 thumb.draw(in:NSRect(x:CGFloat(i%3)*thumbW,y:CGFloat(2-i/3)*thumbH,width:thumbW,height:thumbH))
}
contact.unlockFocus()
let data=NSBitmapImageRep(data:contact.tiffRepresentation!)!.representation(using:.png,properties:[:])!
try data.write(to:render.appendingPathComponent("contacto.png"))
print("PDF generado y renderizado: \(pdf.pageCount) páginas")
